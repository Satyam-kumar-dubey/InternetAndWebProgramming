import json
from dataclasses import dataclass
from typing import Dict, Any, List


def safe_number(value: Any, field_name: str) -> float:
    """Convert to float and reject invalid or negative values (basic safety)."""
    try:
        num = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid number for '{field_name}': {value!r}")
    if num < 0:
        raise ValueError(f"Negative value not allowed for '{field_name}': {num}")
    return num


def calc_progressive_tax(monthly_gross: float) -> float:
    """
    Example progressive monthly tax slabs (you can change these):
    - 0% up to 25,000
    - 5% for 25,001 to 50,000
    - 10% for 50,001 to 100,000
    - 20% above 100,000
    """
    slabs = [
        (25000, 0.00),
        (50000, 0.05),
        (100000, 0.10),
        (float("inf"), 0.20),
    ]

    tax = 0.0
    prev_limit = 0.0
    remaining = monthly_gross

    for limit, rate in slabs:
        chunk = min(remaining, limit - prev_limit)
        if chunk <= 0:
            break
        tax += chunk * rate
        remaining -= chunk
        prev_limit = limit

    return round(tax, 2)


@dataclass
class PayrollResult:
    employee_id: str
    name: str
    gross_pay: float
    total_deductions: float
    tax: float
    net_pay: float


def compute_employee_payroll(emp: Dict[str, Any]) -> PayrollResult:
    emp_id = str(emp.get("id", "")).strip()
    name = str(emp.get("name", "")).strip()
    if not emp_id or not name:
        raise ValueError("Employee must have non-empty 'id' and 'name'")

    pay = emp.get("pay", {})
    base = safe_number(pay.get("base_salary", 0), "base_salary")

    allowances = pay.get("allowances", {}) or {}
    hra = safe_number(allowances.get("hra", 0), "allowances.hra")
    da = safe_number(allowances.get("da", 0), "allowances.da")
    bonus = safe_number(allowances.get("bonus", 0), "allowances.bonus")
    other_allow = safe_number(allowances.get("other", 0), "allowances.other")
    total_allowances = hra + da + bonus + other_allow

    overtime = pay.get("overtime", {}) or {}
    ot_hours = safe_number(overtime.get("hours", 0), "overtime.hours")
    ot_rate = safe_number(overtime.get("rate_per_hour", 0), "overtime.rate_per_hour")
    overtime_pay = ot_hours * ot_rate

    gross = base + total_allowances + overtime_pay
    gross = round(gross, 2)

    deductions = pay.get("deductions", {}) or {}
    pf = safe_number(deductions.get("pf", 0), "deductions.pf")
    prof_tax = safe_number(deductions.get("professional_tax", 0), "deductions.professional_tax")
    insurance = safe_number(deductions.get("insurance", 0), "deductions.insurance")
    other_ded = safe_number(deductions.get("other", 0), "deductions.other")
    total_deductions = round(pf + prof_tax + insurance + other_ded, 2)

    tax = calc_progressive_tax(gross)
    net = round(gross - total_deductions - tax, 2)

    return PayrollResult(
        employee_id=emp_id,
        name=name,
        gross_pay=gross,
        total_deductions=total_deductions,
        tax=tax,
        net_pay=net,
    )


def load_employees(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("employees.json must contain a JSON array of employees")
    return data


def save_report(path: str, report: List[Dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


def print_report(results: List[PayrollResult]) -> None:
    print("\nPAYROLL REPORT")
    print("-" * 72)
    print(f"{'ID':<8} {'Name':<20} {'Gross':>10} {'Deduct':>10} {'Tax':>8} {'Net':>10}")
    print("-" * 72)
    for r in results:
        print(
            f"{r.employee_id:<8} {r.name:<20} "
            f"{r.gross_pay:>10.2f} {r.total_deductions:>10.2f} {r.tax:>8.2f} {r.net_pay:>10.2f}"
        )
    print("-" * 72)


def main():
    input_file = "employees.json"
    output_file = "payroll_report.json"

    employees = load_employees(input_file)

    results: List[PayrollResult] = []
    report_json: List[Dict[str, Any]] = []

    for emp in employees:
        r = compute_employee_payroll(emp)
        results.append(r)
        report_json.append(
            {
                "id": r.employee_id,
                "name": r.name,
                "gross_pay": r.gross_pay,
                "total_deductions": r.total_deductions,
                "tax": r.tax,
                "net_pay": r.net_pay,
            }
        )

    save_report(output_file, report_json)
    print_report(results)
    print(f"\nSaved: {output_file}\n")


if __name__ == "__main__":
    main()