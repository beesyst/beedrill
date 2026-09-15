import beedrill


def test_public_package_surface_is_explicit() -> None:
    assert beedrill.__all__ == ["BeeDrillModule"]
    assert beedrill.BeeDrillModule.__module__ == "beedrill.module"


def test_module_identity_and_initial_authority() -> None:
    module = beedrill.BeeDrillModule()

    assert module.module_id == "beedrill"
    assert module.authority == "read_only"


def test_module_has_no_execution_entrypoint() -> None:
    module = beedrill.BeeDrillModule()

    assert not hasattr(module, "handle")
    assert not hasattr(module, "execute")
    assert not hasattr(module, "run")
