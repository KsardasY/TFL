import sys
from typing import List, Set, Tuple, NoReturn


def arcmul(a11: str, a12: str, a21: str, a22: str, b: str) -> Tuple[str, str]:
    return f"(arcsum (arcmul {a11} {b}31) (arcmul {a12} {b}32))", \
        f"(arcsum (arcmul {a21} {b}31) (arcmul {a22} {b}32))"


def exp_generator(expression: str) -> Tuple[str, str, str, str, str, str]:
    expr1 = expression[0] + "11"
    expr2 = expression[0] + "12"
    expr3 = expression[0] + "21"
    expr4 = expression[0] + "22"
    free_coefs = [(expression[0] + "31", expression[0] + "32")]
    for x in expression[1:]:
        free_coefs.append(arcmul(expr1, expr2, expr3, expr4, x))
        expr1 = f"(arcmul {expr1} {x}11)"
        expr2 = f"(arcmul {expr2} {x}12)"
        expr3 = f"(arcmul {expr3} {x}21)"
        expr4 = f"(arcmul {expr4} {x}22)"
    free_coef1 = free_coefs[0][0]
    free_coef2 = free_coefs[0][1]
    for x in free_coefs[1:]:
        free_coef1 = f"(arcsum {free_coef1} {x[0]})"
        free_coef2 = f"(arcsum {free_coef2} {x[1]})"
    return expr1, expr2, expr3, expr4, free_coef1, free_coef2


def main() -> None:
    print("Введите строки:")
    condition = list(map(str.strip, sys.stdin))
    variables = set()
    lexp = []
    rexp = []
    for string in condition:
        left, right = string.split("->")
        variables |= set(left.strip()) | set(right.strip())
        lexp.append(exp_generator(left.strip()))
        rexp.append(exp_generator(right.strip()))
    make_file(variables, lexp, rexp)


def make_file(
        variables: Set[str],
        lexp: List[Tuple[str, str, str, str, str, str]],
        rexp: List[Tuple[str, str, str, str, str, str]]
) -> NoReturn:
    start = "(set-logic QF_NIA)\n(define-fun arcsum ((a Int) (b Int)) Int (ite (and (>= a b) (not (= a 0))) a b))\n" \
            "(define-fun arcmul ((a Int) (b Int)) Int (ite (and (> a -1) (> b -1)) (+ a b) -1))\n" \
            "(define-fun arcgg ((a Int) (b Int)) Bool (ite (or (> a b) (and (= a -1) (= b -1))) true false))\n"
    with open("model.smt2", "w") as f:
        f.write(start)
        for x in variables:
            f.write(f"(declare-const {x}11 Int)\n")
            f.write(f"(declare-const {x}12 Int)\n")
            f.write(f"(declare-const {x}21 Int)\n")
            f.write(f"(declare-const {x}22 Int)\n")
            f.write(f"(declare-const {x}31 Int)\n")
            f.write(f"(declare-const {x}32 Int)\n")
        for x in variables:
            f.write(f"(assert (> {x}11 0))\n")
            f.write(f"(assert (or (> {x}12 0) (= {x}12 -1)))\n")
            f.write(f"(assert (or (> {x}21 0) (= {x}21 -1)))\n")
            f.write(f"(assert (or (> {x}22 0) (= {x}22 -1)))\n")
            f.write(f"(assert (or (and (> {x}31 0) (> {x}32 -2) (not (= {x}32 0))) (and (= {x}31 0) (= {x}32 0))))\n")
        for l, r in zip(lexp, rexp):
            for x, y in zip(l, r):
                f.write(f"(assert (arcgg {x} {y}))\n")
        f.write("(check-sat)\n(get-model)\n(exit)")


if __name__ == "__main__":
    main()
