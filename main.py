from processor.xgb_result_check import ResultCheck


def main():
    print("Start with bookie_result ms")
    rc = ResultCheck()
    rc.possible_win()
    return print("Done with bookie_result ms")


if __name__ == "__main__":
    main()
