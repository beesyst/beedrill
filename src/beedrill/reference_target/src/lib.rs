// SECURITY: Deliberately vulnerable BeeDrill reference-only test program.
// Never deploy this program to production or mainnet.

use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    program_error::ProgramError,
    pubkey::Pubkey,
};

const STATE_SIZE: usize = 18;
const INITIAL_VAULT_LAMPORTS: u64 = 1_000_000;
const NORMAL_DEPOSIT_LAMPORTS: u64 = 10;
const UNSAFE_WITHDRAW_LAMPORTS: u64 = 100;

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
        1 => normal_deposit(&mut data),
        2 => unsafe_withdraw(&mut data),
        3 => set_breaker(&mut data, true),
        4 => set_breaker(&mut data, false),
        5 => set_containment(&mut data, true),
        6 => set_containment(&mut data, false),
        _ => Err(ProgramError::InvalidInstructionData),
    }
}

fn initialize(data: &mut [u8]) -> ProgramResult {
    data.fill(0);
    data[2..10].copy_from_slice(&INITIAL_VAULT_LAMPORTS.to_le_bytes());
    Ok(())
}

fn normal_deposit(data: &mut [u8]) -> ProgramResult {
    if data[0] != 0 {
        return Err(ProgramError::InvalidArgument);
    }
    let updated = vault_lamports(data)?
        .checked_add(NORMAL_DEPOSIT_LAMPORTS)
        .ok_or(ProgramError::ArithmeticOverflow)?;
    data[2..10].copy_from_slice(&updated.to_le_bytes());
    increment(data, 10)
}

fn unsafe_withdraw(data: &mut [u8]) -> ProgramResult {
    if data[0] != 0 && data[1] == 0 {
        return Err(ProgramError::InvalidArgument);
    }
    let updated = vault_lamports(data)?
        .checked_sub(UNSAFE_WITHDRAW_LAMPORTS)
        .ok_or(ProgramError::InsufficientFunds)?;
    data[2..10].copy_from_slice(&updated.to_le_bytes());
    increment(data, 14)
}

fn set_breaker(data: &mut [u8], paused: bool) -> ProgramResult {
    data[0] = u8::from(paused);
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
    fn initialization_is_canonical() {
        let data = state();
        assert_eq!(vault_lamports(&data).unwrap(), INITIAL_VAULT_LAMPORTS);
        assert_eq!(data[0], 0);
        assert_eq!(data[1], 0);
        assert_eq!(&data[10..], &[0; 8]);
    }

    #[test]
    fn normal_operation_and_unsafe_signal_are_counted() {
        let mut data = state();
        normal_deposit(&mut data).unwrap();
        unsafe_withdraw(&mut data).unwrap();
        assert_eq!(vault_lamports(&data).unwrap(), 999_910);
        assert_eq!(u32::from_le_bytes(data[10..14].try_into().unwrap()), 1);
        assert_eq!(u32::from_le_bytes(data[14..18].try_into().unwrap()), 1);
    }

    #[test]
    fn valid_containment_breaker_blocks_the_unsafe_path() {
        let mut data = state();
        set_breaker(&mut data, true).unwrap();
        assert_eq!(unsafe_withdraw(&mut data), Err(ProgramError::InvalidArgument));
        assert_eq!(vault_lamports(&data).unwrap(), INITIAL_VAULT_LAMPORTS);
    }

    #[test]
    fn broken_containment_leaves_the_vulnerable_path_reachable() {
        let mut data = state();
        set_breaker(&mut data, true).unwrap();
        set_containment(&mut data, true).unwrap();
        unsafe_withdraw(&mut data).unwrap();
        assert_eq!(vault_lamports(&data).unwrap(), 999_900);
        assert_eq!(u32::from_le_bytes(data[14..18].try_into().unwrap()), 1);
    }

    #[test]
    fn reset_restores_the_canonical_state() {
        let mut data = state();
        normal_deposit(&mut data).unwrap();
        unsafe_withdraw(&mut data).unwrap();
        set_breaker(&mut data, true).unwrap();
        set_containment(&mut data, true).unwrap();
        initialize(&mut data).unwrap();
        assert_eq!(data, state());
    }
}

fn set_containment(data: &mut [u8], broken: bool) -> ProgramResult {
    data[1] = u8::from(broken);
    Ok(())
}

fn vault_lamports(data: &[u8]) -> Result<u64, ProgramError> {
    data[2..10]
        .try_into()
        .map(u64::from_le_bytes)
        .map_err(|_| ProgramError::InvalidAccountData)
}

fn increment(data: &mut [u8], offset: usize) -> ProgramResult {
    let count = u32::from_le_bytes(
        data[offset..offset + 4]
            .try_into()
            .map_err(|_| ProgramError::InvalidAccountData)?,
    );
    data[offset..offset + 4].copy_from_slice(
        &count
            .checked_add(1)
            .ok_or(ProgramError::ArithmeticOverflow)?
            .to_le_bytes(),
    );
    Ok(())
}
