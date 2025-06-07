from moc_sim import StableSystem


def print_help():
    print("Available commands:")
    print("  mint_doc <btc>")
    print("  mint_doc_amt <doc>")
    print("  redeem_doc <doc>")
    print("  mint_bpro <btc>")
    print("  redeem_bpro <bpro>")
    print("  set_price <price>")
    print("  advance_time <steps>")
    print("  summary")
    print("  panel")
    print("  help")
    print("  exit")


def main(config_file="config.json"):
    try:
        system = StableSystem.from_config(config_file)
    except FileNotFoundError:
        system = StableSystem()
    print("Interactive Money on Chain simulation")
    print_help()
    while True:
        try:
            line = input("command> ").strip()
        except EOFError:
            break
        if not line:
            continue
        tokens = line.split()
        cmd = tokens[0]
        args = tokens[1:]
        if cmd in ("exit", "quit"):
            break
        try:
            if cmd == "mint_doc" and len(args) == 1:
                system.mint_doc(float(args[0]))
            elif cmd == "mint_doc_amt" and len(args) == 1:
                system.mint_doc_amount(float(args[0]))
            elif cmd == "redeem_doc" and len(args) == 1:
                system.redeem_doc(float(args[0]))
            elif cmd == "mint_bpro" and len(args) == 1:
                system.mint_bpro(float(args[0]))
            elif cmd == "redeem_bpro" and len(args) == 1:
                system.redeem_bpro(float(args[0]))
            elif cmd == "set_price" and len(args) == 1:
                system.set_price(float(args[0]))
            elif cmd == "advance_time" and len(args) == 1:
                system.advance_time(int(args[0]))
            elif cmd == "summary" and len(args) == 0:
                system.summary()
            elif cmd == "panel" and len(args) == 0:
                system.panel()
            elif cmd == "help":
                print_help()
            else:
                print("Unknown command. Type 'help' for instructions.")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    import sys
    config = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    main(config)
