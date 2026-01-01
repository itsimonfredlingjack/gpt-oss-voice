
try:
    from cli.app import CLIApp
    from cli.avatar import MechaCoreAvatar
    from cli.theme import CHIMERA_THEME
    print("Import successful")
    
    app = CLIApp()
    print("App Initialization successful")
    
    if isinstance(app.avatar, MechaCoreAvatar):
        print("Avatar: Mecha-Core Unit 734 [OK]")
    else:
        print(f"Avatar: {type(app.avatar)} [FAIL]")
        

    # Test Render Cycle
    print("Testing Sentry Scan...", end="")
    try:
        app.avatar.render("IDLE")
        print(" [OK]")
    except Exception as e:
        print(f" [FAIL] {e}")
        raise e
    
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
