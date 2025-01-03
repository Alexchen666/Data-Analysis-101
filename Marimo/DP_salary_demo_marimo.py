import marimo

__generated_with = "0.10.7"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # 差分隱私教學

        Ref. https://docs.opendp.org/en/stable/theory/index.html
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 概覽資料""")
    return


@app.cell
def _(pl):
    df = pl.read_csv('Tutorial_Data/salaries.csv')
    return (df,)


@app.cell
def _(df):
    df.head()
    return


@app.cell
def _(df):
    df.shape
    return


@app.cell
def _(df, pl):
    salaries = df.select(pl.col('salary_in_usd')).to_numpy().flatten()
    return (salaries,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 釋出平均數安全嗎?

        現在有一個簡單的服務是釋出 salaries 的平均數，但使用者不能看到整個資料集
        """
    )
    return


@app.cell
def _(np, salaries):
    overall_mean = np.mean(salaries)
    print('平均薪資為', overall_mean, '美元')
    return (overall_mean,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### 還原出特定資料

        如果這個服務可以讓我們知道特定區間的 salaries 平均數與資料筆數，我們就有機會可以還原出特定資料

        假設我們今天要還原資料集中第1筆資料的薪水，我們需要知道

        *   第1筆資料之外的平均數
        *   資料集的資料筆數
        """
    )
    return


@app.cell
def _(np, salaries):
    exact_mean = np.mean(salaries[1:])
    print("第一個人以外的平均薪資為", exact_mean, '美元')

    n_obs = len(salaries)
    print("資料集包含", n_obs, '筆薪資資訊')
    return exact_mean, n_obs


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        #### 差異攻擊

        透過兩次回傳平均數的差異，就可以完成攻擊
        """
    )
    return


@app.cell
def _(exact_mean, n_obs, overall_mean):
    attack_income = overall_mean * n_obs - exact_mean * (n_obs-1)
    print('第一個人的薪資為',round(attack_income), '美元')
    return (attack_income,)


@app.cell
def _(salaries):
    real_income = salaries[0]
    print('第一個人的實際薪資為',real_income, '美元')
    return (real_income,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 保護釋出的平均數

        我們想安全地提供這項平均數計算服務，且也一樣維持彈性與功能，希望**無法從輸出(平均數)來反推或是洩漏輸入(資料集)的相關資訊**，差分隱私是一個很好的工具，可以幫助我們達成這件事情
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### 使用差分隱私保護

        我們剛剛釋出第一筆之外的平均數，但是可以被攻擊並還原，現在我們**使用差分隱私來保護平均數的計算過程**，觀察與原始平均數差異與是否能有效抵禦攻擊
        """
    )
    return


@app.cell
def _(dp):
    def make_dp_mean(salary_bounds, n, epsilon):
      delta = (salary_bounds[1]-salary_bounds[0])/n
      b = delta/epsilon

      clamp_and_resize_data = (
        (dp.vector_domain(dp.atom_domain(T=float)), dp.symmetric_distance()) >>
        dp.t.then_clamp(bounds=salary_bounds) >>
        dp.t.then_resize(size=n, constant=10_000.0)
      )
      mean_measurement = (
        clamp_and_resize_data >>
        dp.t.then_mean() >>
        dp.m.then_laplace(scale=b)
      )
      return mean_measurement
    return (make_dp_mean,)


@app.cell
def _(make_dp_mean, n_obs):
    dp_mean_1 = make_dp_mean((0.0, 750_000.0),n_obs,10)
    dp_mean_2 = make_dp_mean((0.0, 750_000.0),n_obs-1,10)
    return dp_mean_1, dp_mean_2


@app.cell
def _(dp_mean_1, overall_mean, salaries):
    dp_overall_mean = dp_mean_1(salaries)

    print("平均薪資為", overall_mean, '美元')
    print("加入差分隱私後，平均薪資為", dp_overall_mean, '美元')
    print("差異:", overall_mean-dp_overall_mean, '美元')
    return (dp_overall_mean,)


@app.cell
def _(alt, dp_mean_1, mo, np, overall_mean, pl, salaries):
    dp_overall_mean_ = np.array([dp_mean_1(salaries) for _ in range(1000)])
    df_dp = pl.DataFrame({'DP_Mean': dp_overall_mean_})

    hist_dp = alt.Chart(df_dp).mark_bar().encode(
        alt.X('DP_Mean', bin=alt.Bin(maxbins=100), title='保護後的資料集平均數'),
        y='count()'
    )

    rule = alt.Chart().mark_rule(color='red').encode(
        x=alt.X(datum=overall_mean),
        size=alt.value(3)
    )

    annot = alt.Chart().mark_text(
        text='資料集平均數',
        color='red',
        align='left',
        baseline='middle',
        dx=7
    ).encode(
        x=alt.X(datum=overall_mean),
        y=alt.value(10)
    )

    mo.ui.altair_chart(hist_dp + rule + annot)
    return annot, df_dp, dp_overall_mean_, hist_dp, rule


@app.cell
def _(dp_mean_2, exact_mean, salaries):
    dp_exact_mean = dp_mean_2(salaries[1:])

    print("第一個人以外的平均薪資為", exact_mean, '美元')
    print("加入差分隱私後，第一個人以外的平均薪資為", dp_exact_mean, '美元')
    print("差異:", exact_mean-dp_exact_mean, '美元')
    return (dp_exact_mean,)


@app.cell
def _(alt, dp_mean_2, exact_mean, mo, np, pl, salaries):
    dp_exact_mean_ = np.array([dp_mean_2(salaries[1:]) for _ in range(1000)])
    df_dp_exact = pl.DataFrame({'DP_Mean': dp_exact_mean_})

    hist_dp_exact = alt.Chart(df_dp_exact).mark_bar().encode(
        alt.X('DP_Mean', bin=alt.Bin(maxbins=100), title='保護後的第一筆之外的平均數'),
        y='count()'
    )

    rule_exact = alt.Chart().mark_rule(color='red').encode(
        x=alt.X(datum=exact_mean),
        size=alt.value(3)
    )

    annot_exact = alt.Chart().mark_text(
        text='第一筆之外的平均數',
        color='red',
        align='left',
        baseline='middle',
        dx=7
    ).encode(
        x=alt.X(datum=exact_mean),
        y=alt.value(10)
    )

    mo.ui.altair_chart(hist_dp_exact + rule_exact + annot_exact)
    return (
        annot_exact,
        df_dp_exact,
        dp_exact_mean_,
        hist_dp_exact,
        rule_exact,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### 差分隱私保護成效

        我們可以初步看到經過差分隱私保護的平均數依然與原始平均數相近，但採用相同差異攻擊來還原第一筆資料時，使用保護後的平均數來進行攻擊，還原第一筆資料的效果就有明顯差距，達成抵抗差異攻擊的效果
        """
    )
    return


@app.cell
def _(dp_exact_mean, dp_overall_mean, n_obs, real_income):
    attack_income_1 = dp_overall_mean * n_obs - dp_exact_mean * (n_obs - 1)
    print('加入差分隱私後，推測的第一個人薪資為', attack_income_1, '美元')
    print('第一個人的實際薪資為', real_income, '美元')
    print('差異:', attack_income_1 - real_income, '美元')
    return (attack_income_1,)


@app.cell
def _(alt, dp_exact_mean_, dp_overall_mean_, mo, n_obs, pl, real_income):
    attack_income_ = dp_overall_mean_ * n_obs - dp_exact_mean_ * (n_obs - 1)
    df_attack = pl.DataFrame({'Attack Income': attack_income_})

    hist_dp_attack = alt.Chart(df_attack).mark_bar().encode(
        alt.X('Attack Income', bin=alt.Bin(maxbins=100), title='還原保護後的第一筆資料'),
        y='count()'
    )

    rule_attack = alt.Chart().mark_rule(color='red').encode(
        x=alt.X(datum=real_income),
        size=alt.value(3)
    )

    annot_attack = alt.Chart().mark_text(
        text='真實第一筆資料',
        color='red',
        align='left',
        baseline='middle',
        dx=7
    ).encode(
        x=alt.X(datum=real_income),
        y=alt.value(10)
    )

    mo.ui.altair_chart(hist_dp_attack + rule_attack + annot_attack)
    return (
        annot_attack,
        attack_income_,
        df_attack,
        hist_dp_attack,
        rule_attack,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 附錄：載入套件""")
    return


@app.cell
def _():
    import numpy as np
    import polars as pl
    import warnings
    import opendp.prelude as dp
    import altair as alt
    import marimo as mo

    dp.enable_features('contrib')

    # hide warning created by outstanding scipy.stats issue
    warnings.simplefilter(action='ignore', category=FutureWarning)
    return alt, dp, mo, np, pl, warnings


if __name__ == "__main__":
    app.run()
