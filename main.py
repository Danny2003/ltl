import argparse
from ltl_parser import parser
from ts import parse_transition_system
from gnba_cons import construct_gnba_from_ltl_formula
from gnba_detect import gnba_to_nba, product_construction, nested_dfs

def parse_ltl_formulas(input_str):
    """
    parse the LTL formulas into a list of global formulas and a list of state formulas
    """
    lines = input_str.strip().split('\n')
    A, B = map(int, lines[0].split())
    global_formulas = [lines[i] for i in range(1, 1 + A)]
    state_formulas = []
    for i in range(1 + A, 1 + A + B):
        parts = lines[i].split()
        state = int(parts[0])
        formula = ' '.join(parts[1:])
        state_formulas.append((state, formula))
    return global_formulas, state_formulas

def main(ts_file, ltl_file, detail):
    with open(ts_file, 'r') as f:
        ts_input = f.read()

    with open(ltl_file, 'r') as f:
        ltl_input = f.read()

    # Parsing the inputs
    ts = parse_transition_system(ts_input)
    if detail:
        print("parsing the transition system:")
        print("states: ", end = "")
        for s in ts.states:
            if s == ts.states[-1]:
                print(f"s_{s}")
            else:
                print(f"s_{s}", end = " ")
        print("initial states: ", end = "")
        for s in ts.initial_states:
            if s == ts.initial_states[-1]:
                print(f"s_{s}")
            else:
                print(f"s_{s}", end = " ")
        print("actions: ", end = "")
        for a in ts.actions:
            if a == ts.actions[-1]:
                print(a)
            else:
                print(a, end = " ")
        print("transitions:")
        for s in ts.transitions:
            for a in ts.transitions[s]:
                for s_prime in ts.transitions[s][a]:
                    print(f"s_{s} with action {a} --> s_{s_prime}")
        print("propositions: ", end = "")
        for p in ts.propositions:
            if p == ts.propositions[-1]:
                print(p)
            else:
                print(p, end = " ")
        print("labeling:")
        for s in ts.states:
            if ts.labeling[s]:
                print(f"s_{s} is labeled with propositions: ", end = "")
                for l in ts.labeling[s]:
                    print(l, end = " ")
                print()
            else:
                print(f"s_{s} is labeled with no propositions")
        print()
    global_formulas, state_formulas = parse_ltl_formulas(ltl_input)

    for formula in global_formulas:
        if detail:
            print(f"start from initial states of the ts\nLTL formula:\n{parser.parse(formula)}")
        gnba, props = construct_gnba_from_ltl_formula(('not', parser.parse((formula))), detail)
        nba = gnba_to_nba(gnba, props, detail)
        product = product_construction(ts.copy(), nba, props, detail)
        result = nested_dfs(product, nba, detail)
        if result != None:
            print(result)

    for (initial_state, formula) in state_formulas:
        if detail:
            print(f"initial state: {initial_state}\nLTL formula:\n{parser.parse(formula)}")
        gnba, props = construct_gnba_from_ltl_formula(('not', parser.parse((formula))), detail)
        nba = gnba_to_nba(gnba, props, detail)
        new_ts = ts.copy()
        new_ts.initial_states = [initial_state]
        product = product_construction(new_ts, nba, props, detail)
        result = nested_dfs(product, nba, detail)
        if result != None:
            print(result)

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="LTL Model Checking")
    arg_parser.add_argument("ts_file", help="File containing the transition system")
    arg_parser.add_argument("ltl_file", help="File containing the LTL formulas")
    # 添加 -d 参数，当 -d 被使用时，将输出 parser 结果和反例信息
    arg_parser.add_argument('-d', action='store_const', const=1, default=0)
    # 添加 -f 参数，当 -f 被使用时，将输出到文件，而不是输出到控制台，-f 后面必须有文件名
    arg_parser.add_argument('-f', action='store', dest='output_file', type=str)
    args = arg_parser.parse_args()

    if args.output_file:
        import sys
        with open(args.output_file, 'w') as f:
            # 保存原始的 stdout
            original_stdout = sys.stdout

            # 重定向 stdout 到文件
            sys.stdout = f

            if args.d:
                main(args.ts_file, args.ltl_file, args.d)
            else:
                main(args.ts_file, args.ltl_file, 0)
    else:
        if args.d:
            main(args.ts_file, args.ltl_file, args.d)
        else:
            main(args.ts_file, args.ltl_file, 0)