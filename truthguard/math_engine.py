"""
Mathematical & Symbolic Logic Evaluation Engine for TruthGuard
Detects, evaluates, and verifies arithmetic, algebraic, and numeric statements.
Provides undeniable ground-truth evidence, exact error span isolation,
and minimal grounded corrections for mathematical hallucinations.
"""

import re
import math
import ast
from typing import Dict, Any, Optional, Tuple, List


# Safe math operators mapping
SAFE_OPERATORS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b if b != 0 else float('inf'),
    ast.FloorDiv: lambda a, b: a // b if b != 0 else float('inf'),
    ast.Mod: lambda a, b: a % b if b != 0 else float('inf'),
    ast.Pow: lambda a, b: a ** b if abs(b) <= 20 else float('inf'),
    ast.USub: lambda a: -a,
    ast.UAdd: lambda a: +a,
}

WORD_TO_OP = {
    "plus": "+",
    "minus": "-",
    "times": "*",
    "multiplied by": "*",
    "divided by": "/",
    "over": "/",
    "equals": "=",
    "equal to": "=",
    "is equal to": "=",
    "is": "=",
}


def _eval_ast_node(node):
    """Safely evaluates an AST expression node with only mathematical operators."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError("Non-numeric constant")
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            left = _eval_ast_node(node.left)
            right = _eval_ast_node(node.right)
            return SAFE_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported binary operator: {op_type}")
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            operand = _eval_ast_node(node.operand)
            return SAFE_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type}")
    elif isinstance(node, ast.Call):
        # Support sqrt, abs, round
        func_name = getattr(node.func, 'id', '')
        if func_name == 'sqrt' and len(node.args) == 1:
            arg = _eval_ast_node(node.args[0])
            return math.sqrt(arg) if arg >= 0 else float('nan')
        elif func_name == 'abs' and len(node.args) == 1:
            return abs(_eval_ast_node(node.args[0]))
        elif func_name == 'round' and len(node.args) >= 1:
            arg = _eval_ast_node(node.args[0])
            return round(arg)
        raise ValueError(f"Unsupported function call: {func_name}")
    else:
        raise ValueError(f"Unsupported AST node: {type(node)}")


def safe_eval_math_expr(expr_str: str) -> Optional[float]:
    """Safely evaluates a pure arithmetic string expression (e.g. '2 + 2', '10 * 5 - 3')."""
    # Clean expression
    clean = expr_str.strip().replace('^', '**').replace('×', '*').replace('÷', '/')
    # Remove leading/trailing non-math punctuation
    clean = re.sub(r'^[^\d\(\-\+]+', '', clean)
    clean = re.sub(r'[^\d\)]+$', '', clean)
    if not clean:
        return None
    try:
        parsed = ast.parse(clean, mode='eval')
        val = _eval_ast_node(parsed.body)
        if math.isnan(val) or math.isinf(val):
            return None
        return val
    except Exception:
        return None


class MathEngine:
    """Detects and verifies mathematical and arithmetic assertions in claims."""

    @staticmethod
    def is_math_claim(text: str) -> bool:
        """Determines if text contains an arithmetic equation or numeric equality assertion."""
        # Check standard equation: e.g. 2+2=7, 10 * 5 = 50, x + y = z
        if re.search(r'[\d\.\)]\s*[\+\-\*\/\^×÷]\s*[\d\.\(].*?[=\=\!\<\>]', text):
            return True
        if re.search(r'\b\d+\s*[\+\-\*\/]\s*\d+\s*=', text):
            return True
        # Check natural language arithmetic: "2 plus 2 is 7", "sum of 2 and 2 is 7"
        if re.search(r'\b(?:sum|difference|product|quotient)\s+of\b', text, re.IGNORECASE):
            return True
        if re.search(r'\b\d+\s+(?:plus|minus|times|divided\s+by)\s+\d+\s+(?:equals?|is)\s+\d+\b', text, re.IGNORECASE):
            return True
        if re.search(r'^\s*[\(\d\.\s\+\-\*\/\^\=]+\s*$', text) and ('=' in text or '==' in text):
            return True
        return False

    @classmethod
    def evaluate_claim(cls, claim_text: str) -> Optional[Dict[str, Any]]:
        """
        Evaluates a mathematical claim.
        Returns None if the claim is not mathematical.
        Returns a verification dict if evaluated:
            - is_math: True
            - is_correct: bool
            - lhs_str: str
            - rhs_str: str
            - lhs_val: float
            - rhs_val: float
            - ground_truth_answer: str
            - evidence_sentence: str
            - suggested_edit: str
            - error_span: Optional[Dict]
        """
        claim_stripped = claim_text.strip().rstrip('.')

        # Pattern 1: Direct equation: LHS = RHS (or ==, !=, <=, >=, <, >)
        # Matches e.g. "2+2=7", "2 + 2 = 7", "10 * 5 == 50"
        eq_match = re.search(r'^(.*?)\s*(=|==|!=)\s*([^\=\!\<\>]+)$', claim_stripped)
        
        # Also handle claims where equation is embedded: e.g. "It is known that 2+2=7."
        if not eq_match:
            eq_match = re.search(r'(\b[\d\.\s\+\-\*\/\^\(\)]+?)\s*(=|==)\s*(-?[\d\.]+)', claim_stripped)

        if eq_match:
            lhs_raw = eq_match.group(1).strip()
            operator = eq_match.group(2).strip()
            rhs_raw = eq_match.group(3).strip()

            lhs_val = safe_eval_math_expr(lhs_raw)
            rhs_val = safe_eval_math_expr(rhs_raw)

            if lhs_val is not None and rhs_val is not None:
                # Check equality
                is_equal = math.isclose(lhs_val, rhs_val, rel_tol=1e-5, abs_tol=1e-5)
                is_correct = is_equal if operator in ('=', '==') else (not is_equal)

                # Format true value nicely
                if lhs_val.is_integer():
                    correct_val_str = str(int(lhs_val))
                else:
                    correct_val_str = f"{lhs_val:.4g}"

                if is_correct:
                    evidence = f"By fundamental arithmetic rules, {lhs_raw} = {correct_val_str}. The statement '{claim_text}' is mathematically sound and true."
                    suggested_edit = claim_text
                    error_span = None
                else:
                    evidence = (
                        f"By standard arithmetic rules, {lhs_raw} equals {correct_val_str}, not {rhs_raw}. "
                        f"Therefore, the statement '{claim_text.strip()}' is mathematically false."
                    )
                    # Create corrected version matching original spacing
                    if f'= {rhs_raw}' in claim_stripped:
                        suggested_edit = claim_stripped.replace(f'= {rhs_raw}', f'= {correct_val_str}')
                    elif f'={rhs_raw}' in claim_stripped:
                        suggested_edit = claim_stripped.replace(f'={rhs_raw}', f'={correct_val_str}')
                    elif f'== {rhs_raw}' in claim_stripped:
                        suggested_edit = claim_stripped.replace(f'== {rhs_raw}', f'== {correct_val_str}')
                    elif f'=={rhs_raw}' in claim_stripped:
                        suggested_edit = claim_stripped.replace(f'=={rhs_raw}', f'=={correct_val_str}')
                    else:
                        suggested_edit = re.sub(
                            rf'(=|==)\s*{re.escape(rhs_raw)}',
                            f"\\1 {correct_val_str}",
                            claim_stripped
                        )
                    if claim_text.strip().endswith('.') and not suggested_edit.endswith('.'):
                        suggested_edit += '.'

                    # Find exact error span in claim_text
                    pos = claim_text.rfind(rhs_raw)
                    if pos != -1:
                        error_span = {
                            "text": rhs_raw,
                            "char_start": pos,
                            "char_end": pos + len(rhs_raw)
                        }
                    else:
                        error_span = {
                            "text": claim_text,
                            "char_start": 0,
                            "char_end": len(claim_text)
                        }

                return {
                    "is_math": True,
                    "is_correct": is_correct,
                    "lhs_str": lhs_raw,
                    "rhs_str": rhs_raw,
                    "lhs_val": lhs_val,
                    "rhs_val": rhs_val,
                    "correct_val_str": correct_val_str,
                    "evidence_sentence": evidence,
                    "suggested_edit": suggested_edit,
                    "error_span": error_span
                }

        # Pattern 2: Natural language arithmetic: "two plus two equals seven", "sum of 2 and 2 is 7"
        nl_match = re.search(
            r'(\b\d+)\s+(plus|minus|times|divided\s+by)\s+(\d+)\s+(?:equals?|is)\s+(\d+)\b',
            claim_stripped,
            re.IGNORECASE
        )
        if nl_match:
            n1 = float(nl_match.group(1))
            op_word = nl_match.group(2).lower()
            n2 = float(nl_match.group(3))
            stated_res = float(nl_match.group(4))

            if "plus" in op_word:
                true_val = n1 + n2
                sym_op = "+"
            elif "minus" in op_word:
                true_val = n1 - n2
                sym_op = "-"
            elif "times" in op_word:
                true_val = n1 * n2
                sym_op = "*"
            else:
                true_val = n1 / n2 if n2 != 0 else float('inf')
                sym_op = "/"

            is_correct = math.isclose(true_val, stated_res, rel_tol=1e-5, abs_tol=1e-5)
            true_str = str(int(true_val)) if true_val.is_integer() else f"{true_val:.4g}"
            stated_str = nl_match.group(4)

            if is_correct:
                evidence = f"By arithmetic definition, {int(n1)} {sym_op} {int(n2)} = {true_str}. The claim is correct."
                suggested_edit = claim_text
                error_span = None
            else:
                evidence = f"By standard arithmetic rules, {int(n1)} {sym_op} {int(n2)} equals {true_str}, which directly contradicts the claim of {stated_str}."
                # Replace stated result with true result
                suggested_edit = re.sub(rf'\b{re.escape(stated_str)}\b', true_str, claim_stripped)
                if not suggested_edit.endswith('.'):
                    suggested_edit += '.'
                pos = claim_text.rfind(stated_str)
                error_span = {
                    "text": stated_str,
                    "char_start": pos if pos != -1 else 0,
                    "char_end": (pos + len(stated_str)) if pos != -1 else len(claim_text)
                }

            return {
                "is_math": True,
                "is_correct": is_correct,
                "lhs_str": f"{n1} {sym_op} {n2}",
                "rhs_str": stated_str,
                "lhs_val": true_val,
                "rhs_val": stated_res,
                "correct_val_str": true_str,
                "evidence_sentence": evidence,
                "suggested_edit": suggested_edit,
                "error_span": error_span
            }

        # Pattern 3: Natural language sum/product/difference/quotient:
        # e.g., "The sum of 15 and 27 equals 42", "difference between 10 and 4 is 6"
        sum_match = re.search(
            r'\b(sum|difference|product|quotient)\s+(?:of|between)\s+(\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)\s+(?:equals?|is)\s+(\d+(?:\.\d+)?)\b',
            claim_stripped,
            re.IGNORECASE
        )
        if sum_match:
            op_word = sum_match.group(1).lower()
            n1 = float(sum_match.group(2))
            n2 = float(sum_match.group(3))
            stated_res = float(sum_match.group(4))

            if op_word == "sum":
                true_val = n1 + n2
                sym_op = "+"
            elif op_word == "difference":
                true_val = n1 - n2
                sym_op = "-"
            elif op_word == "product":
                true_val = n1 * n2
                sym_op = "*"
            else:
                true_val = n1 / n2 if n2 != 0 else float('inf')
                sym_op = "/"

            is_correct = math.isclose(true_val, stated_res, rel_tol=1e-5, abs_tol=1e-5)
            true_str = str(int(true_val)) if true_val.is_integer() else f"{true_val:.4g}"
            stated_str = sum_match.group(4)

            if is_correct:
                evidence = f"By arithmetic definition, the {op_word} of {int(n1) if n1.is_integer() else n1} and {int(n2) if n2.is_integer() else n2} is {true_str}. The claim is correct."
                suggested_edit = claim_text
                error_span = None
            else:
                evidence = f"By standard arithmetic rules, the {op_word} of {int(n1) if n1.is_integer() else n1} and {int(n2) if n2.is_integer() else n2} equals {true_str}, which directly contradicts the claim of {stated_str}."
                suggested_edit = re.sub(rf'\b{re.escape(stated_str)}\b', true_str, claim_stripped)
                if not suggested_edit.endswith('.'):
                    suggested_edit += '.'
                pos = claim_text.rfind(stated_str)
                error_span = {
                    "text": stated_str,
                    "char_start": pos if pos != -1 else 0,
                    "char_end": (pos + len(stated_str)) if pos != -1 else len(claim_text)
                }

            return {
                "is_math": True,
                "is_correct": is_correct,
                "lhs_str": f"{n1} {sym_op} {n2}",
                "rhs_str": stated_str,
                "lhs_val": true_val,
                "rhs_val": stated_res,
                "correct_val_str": true_str,
                "evidence_sentence": evidence,
                "suggested_edit": suggested_edit,
                "error_span": error_span
            }

        return None
