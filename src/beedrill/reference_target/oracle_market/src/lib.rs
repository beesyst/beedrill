// SECURITY: Deliberately vulnerable BeeDrill reference-only test program.
// Never deploy this program to production or mainnet.

use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    program_error::ProgramError,
    pubkey::Pubkey,
    entrypoint::ProgramResult,
};

const STATE_SIZE: usize = 25;
const CANONICAL_PRICE_MICRO_USD: u64 = 1_000_000;
const MANIPULATED_PRICE_MICRO_USD: u64 = 2_000_000;
const INITIAL_DEBT_MICRO_USDC: u64 = 50_000_000;
const INITIAL_RESERVE_MICRO_USDC: u64 = 100_000_000;
const BORROW_INCREMENT_MICRO_USDC: u64 = 25_000_000;
const COLLATERAL_UNITS: u64 = 100;
const LTV_BPS: u64 = 5_000;

entrypoint!(process_instruction);

fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let state = next_account_info(&mut accounts.iter())?;
    if state.owner != program_id || !state.is_writable {
        return Err(ProgramError::InvalidAccountData);
    }
    let instruction = instruction_data
        .first()
        .ok_or(ProgramError::InvalidInstructionData)?;
    let mut data = state.try_borrow_mut_data()?;
    if data.len() != STATE_SIZE {
        return Err(ProgramError::InvalidAccountData);
    }
    match *instruction {
        0 => initialize(&mut data),
        1 => manipulate_oracle(&mut data),
        2 => unsafe_borrow(&mut data),
        3 => set_borrowing_blocked(&mut data, true),
        4 => set_borrowing_blocked(&mut data, false),
        _ => Err(ProgramError::InvalidInstructionData),
    }
}

fn initialize(data: &mut [u8]) -> ProgramResult {
    data.fill(0);
    write_u64(data, 1, CANONICAL_PRICE_MICRO_USD)?;
    write_u64(data, 9, INITIAL_DEBT_MICRO_USDC)?;
    write_u64(data, 17, INITIAL_RESERVE_MICRO_USDC)
}

fn manipulate_oracle(data: &mut [u8]) -> ProgramResult {
    if price(data)? != CANONICAL_PRICE_MICRO_USD {
        return Err(ProgramError::InvalidArgument);
    }
    write_u64(data, 1, MANIPULATED_PRICE_MICRO_USD)
}

fn unsafe_borrow(data: &mut [u8]) -> ProgramResult {
    if data[0] != 0 {
        return Err(ProgramError::InvalidArgument);
    }
    let debt = debt(data)?;
    let reserve = reserve(data)?;
    let next_debt = debt
        .checked_add(BORROW_INCREMENT_MICRO_USDC)
        .ok_or(ProgramError::ArithmeticOverflow)?;
    if next_debt > debt_limit(price(data)?)? {
        return Err(ProgramError::InvalidArgument);
    }
    let next_reserve = reserve
        .checked_sub(BORROW_INCREMENT_MICRO_USDC)
        .ok_or(ProgramError::InsufficientFunds)?;
    write_u64(data, 9, next_debt)?;
    write_u64(data, 17, next_reserve)
}

fn set_borrowing_blocked(data: &mut [u8], blocked: bool) -> ProgramResult {
    data[0] = u8::from(blocked);
    Ok(())
}

fn debt_limit(price_micro_usd: u64) -> Result<u64, ProgramError> {
    COLLATERAL_UNITS
        .checked_mul(price_micro_usd)
        .and_then(|value| value.checked_mul(LTV_BPS))
        .and_then(|value| value.checked_div(10_000))
        .ok_or(ProgramError::ArithmeticOverflow)
}

fn price(data: &[u8]) -> Result<u64, ProgramError> {
    read_u64(data, 1)
}

fn debt(data: &[u8]) -> Result<u64, ProgramError> {
    read_u64(data, 9)
}

fn reserve(data: &[u8]) -> Result<u64, ProgramError> {
    read_u64(data, 17)
}

fn read_u64(data: &[u8], offset: usize) -> Result<u64, ProgramError> {
    data[offset..offset + 8]
        .try_into()
        .map(u64::from_le_bytes)
        .map_err(|_| ProgramError::InvalidAccountData)
}

fn write_u64(data: &mut [u8], offset: usize, value: u64) -> ProgramResult {
    data[offset..offset + 8].copy_from_slice(&value.to_le_bytes());
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn state() -> [u8; STATE_SIZE] {
        let mut data = [0; STATE_SIZE];
        initialize(&mut data).unwrap();
        data
    }

    #[test]
    fn canonical_state_has_the_unmanipulated_debt_limit() {
        let data = state();
        assert_eq!(price(&data).unwrap(), CANONICAL_PRICE_MICRO_USD);
        assert_eq!(debt(&data).unwrap(), INITIAL_DEBT_MICRO_USDC);
        assert_eq!(reserve(&data).unwrap(), INITIAL_RESERVE_MICRO_USDC);
        assert_eq!(debt_limit(price(&data).unwrap()).unwrap(), 50_000_000);
    }

    #[test]
    fn manipulated_price_allows_two_fixed_unsafe_borrows() {
        let mut data = state();
        manipulate_oracle(&mut data).unwrap();
        unsafe_borrow(&mut data).unwrap();
        set_borrowing_blocked(&mut data, false).unwrap();
        unsafe_borrow(&mut data).unwrap();
        assert_eq!(debt(&data).unwrap(), 100_000_000);
        assert_eq!(reserve(&data).unwrap(), 50_000_000);
    }

    #[test]
    fn broken_containment_keeps_borrowing_open() {
        let mut data = state();
        manipulate_oracle(&mut data).unwrap();
        unsafe_borrow(&mut data).unwrap();
        set_borrowing_blocked(&mut data, false).unwrap();
        assert_eq!(unsafe_borrow(&mut data), Ok(()));
        assert_eq!(debt(&data).unwrap(), 100_000_000);
        assert_eq!(reserve(&data).unwrap(), 50_000_000);
    }

    #[test]
    fn containment_blocks_the_second_identical_borrow() {
        let mut data = state();
        manipulate_oracle(&mut data).unwrap();
        unsafe_borrow(&mut data).unwrap();
        set_borrowing_blocked(&mut data, true).unwrap();
        assert_eq!(unsafe_borrow(&mut data), Err(ProgramError::InvalidArgument));
        assert_eq!(debt(&data).unwrap(), 75_000_000);
        assert_eq!(reserve(&data).unwrap(), 75_000_000);
    }
}
