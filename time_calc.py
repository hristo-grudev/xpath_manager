def calc_time():
    implement = int(input("Implementations: "))
    maint = int(input("Maintenances: "))
    evals = int(input("Evaluations: "))
    time = int(input("Time(Min, default is 450): ") or 450)
    total_time = round(implement * 10 + maint * 6 + evals * 3.33)
    ratio = total_time / time
    implement_time = round(round((implement * 10) / ratio) / 5) * 5
    maint_time = round(round((maint * 6) / ratio) / 5) * 5
    eval_time = time - implement_time - maint_time

    print(f"Your real time:{total_time}")

    print(f"Implement: {implement} - {implement_time}")
    print(f"Maint: {maint} - {maint_time}")
    print(f"Eval: {evals} - {eval_time}")


if __name__ == "__main__":
    calc_time()
