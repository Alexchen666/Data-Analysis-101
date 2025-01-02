import marimo

__generated_with = "0.10.9"
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


@app.cell
def _(BarWidget, mo):
    widget = mo.ui.anywidget(BarWidget(height=200, width=700, n_bins=20, 
                                       collection_names=['年薪（萬）'], y_min=0, y_max=200))
    return (widget,)


@app.cell(hide_code=True)
def _(mo, widget):
    mo.md(f'''---

    ## 創建資料

    設定 20 位員工的年薪。橫軸為員工編號，從 0 開始到 19，共 20 位員工。縱軸則為每位員工對應的年薪，單位為萬元。

    {widget}
    ''')
    return


@app.cell
def _(pl, widget):
    df = widget.data_as_polars.select(pl.col('bin').cast(pl.Int32).alias('員工編號'),
                                pl.col('value').round().cast(pl.Int32).alias('年薪（萬）'))
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(f'''根據你設定的值，每位員工的薪水資訊如下：''')
    return


@app.cell(hide_code=True)
def _(df):
    df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(f'''對應的敘述性統計顯示如下：''')
    return


@app.cell(hide_code=True)
def _(df, pl):
    df.select(pl.col('年薪（萬）')).describe()
    return


@app.cell
def _(df, pl):
    salaries = df.select(pl.col('年薪（萬）')).to_numpy().flatten()
    return (salaries,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ---

        ## 釋出平均數安全嗎?

        假設 HR 今天推出一項簡單的服務，可以查詢員工年薪的平均數，但使用者不能看到資料集本身，同時為了防止使用者可以看到個人資料，設計者還加入了一個條件：一次必須選取五位以上的員工。

        你認為這項服務安全嗎？有沒有可能洩漏個人資訊呢？

        我們來試用看看這項服務。
        """
    )
    return


@app.cell
def _(mo):
    options = [str(i) for i in range(20)]
    multiselect = mo.ui.multiselect(options=options, label='請選擇員工編號（一次需選取五位以上員工）：')
    return multiselect, options


@app.cell
def _(mo, multiselect):
    mo.hstack([multiselect, mo.md(f'您已選擇：{multiselect.value}')])
    return


@app.cell
def _(mo, multiselect, np, salaries):
    if len(multiselect.value) < 5:
        mo.output.replace(mo.md('請選擇五位以上的員工編號'))
    else:
        ind = np.array(multiselect.value, dtype='int')
        mo.output.replace(mo.md(f'這些員工的平均年薪為 {np.mean(salaries[ind]):.2f} 萬元'))
    return (ind,)


@app.cell
def _(mo):
    input_salary_mean = mo.ui.number(start=0, stop=200, step=0.01, label='請輸入所有人的年薪平均數：')
    input_exclude_salary_mean = mo.ui.number(start=0, stop=200, step=0.01, label='請輸入第一個人以外的年薪平均數：')
    button_check_ans = mo.ui.run_button(label='確認答案', kind='success')
    return button_check_ans, input_exclude_salary_mean, input_salary_mean


@app.cell
def _(input_exclude_salary_mean, input_salary_mean):
    calculated_ans = round(input_salary_mean.value * 20 - input_exclude_salary_mean.value * 19)
    return (calculated_ans,)


@app.cell(hide_code=True)
def _(
    button_check_ans,
    calculated_ans,
    input_exclude_salary_mean,
    input_salary_mean,
    mo,
):
    mo.md(
        f"""
        ---
        
        ### 還原出特定資料

        你也許發現了，儘管在此服務中僅提供薪資平均數，但我們仍可以還原出特定資料。假設我們今天要還原第 1 位員工（編號為 0）的薪水，我們只需要知道：

        * 所有人的年薪平均
        * 第 1 位員工之外的年薪平均
        * 總員工數

        就可以輕易達成。請利用下方的計算機計算出第 1 位員工的年薪。

        1. {input_salary_mean}

        2. {input_exclude_salary_mean}

        第 1 位員工的年薪為 {calculated_ans} 萬元

        按下下方按鈕，確認答案。

        {button_check_ans}
        """
    )
    return


@app.cell
def _(button_check_ans, calculated_ans, mo, salaries):
    if button_check_ans.value:
        mo.output.replace(mo.md(f'你的答案是 {calculated_ans} 萬元，正確答案是 {salaries[0]} 萬元'))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""這種得知個人隱私資訊的方式，我們稱為「差異攻擊」：僅需透過兩次回傳平均數的差異，就可以完成攻擊。""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ---

        ## 保護釋出的平均數

        如果我們想安全地提供這項平均數計算服務，維持一樣的彈性與功能，並且**無法從輸出(平均數)來反推或是洩漏輸入(資料集)的相關資訊**，我們可以使用差分隱私來達成。在詳細介紹以前，我們先來看看差分隱私可以做到什麼。
        """
    )
    return


@app.cell
def _(dp):
    def make_dp_mean(salary_bounds, n, epsilon):
      delta = (salary_bounds[1]-salary_bounds[0])/n
      b = delta/epsilon

      # clamp_and_resize_data = (
      #   (dp.vector_domain(dp.atom_domain(T=float)), dp.symmetric_distance()) >>
      #   dp.t.then_clamp(bounds=salary_bounds) >>
      #   dp.t.then_resize(size=n, constant=100.0)
      # )
      mean_measurement = (
        (dp.vector_domain(dp.atom_domain(T=float, bounds=salary_bounds), size=n), dp.symmetric_distance()) >>
        dp.t.then_mean() >>
        dp.m.then_laplace(scale=b)
      )
      return mean_measurement
    return (make_dp_mean,)


@app.cell
def _(make_dp_mean, salaries):
    n_obs = len(salaries)
    dp_mean_1 = make_dp_mean((0.0, 200.0),n_obs,10)
    dp_mean_2 = make_dp_mean((0.0, 200.0),n_obs-1,10)
    return dp_mean_1, dp_mean_2, n_obs


@app.cell
def _(mo):
    button_dp_overall = mo.ui.run_button(label='差分隱私，啟動！', kind='success')
    return (button_dp_overall,)


@app.cell(hide_code=True)
def _(button_dp_overall, mo):
    mo.md(
        f"""
        ### 使用差分隱私保護

        在前面的實驗中，我們成功得知第一位員工的年薪。現在我們**使用差分隱私來保護平均數的計算過程**，觀察是否能有效抵禦攻擊。

        ---

        ### 所有員工的年薪平均數

        {button_dp_overall}
        """
    )
    return


@app.cell
def _(button_dp_overall, dp_mean_1, np, salaries):
    overall_mean = np.mean(salaries)
    dp_overall_mean = dp_mean_1(salaries) if button_dp_overall.value else 0
    return dp_overall_mean, overall_mean


@app.cell
def _(dp_overall_mean, mo, overall_mean):
    stat_mean_salaries = mo.stat(label='所有員工的平均年薪', value=overall_mean, caption='萬元')
    stat_mean_salaries_dp = mo.stat(label='所有員工的平均年薪（差分隱私）', value=dp_overall_mean, caption='萬元')
    stat_mean_diff = mo.stat(label='差異', value=overall_mean-dp_overall_mean, caption='萬元')

    mo.hstack([stat_mean_salaries, stat_mean_salaries_dp, stat_mean_diff])
    return stat_mean_diff, stat_mean_salaries, stat_mean_salaries_dp


@app.cell
def _(
    alt,
    button_dp_overall,
    dp_mean_1,
    mo,
    np,
    overall_mean,
    pl,
    salaries,
):
    dp_overall_mean_ = np.array([dp_mean_1(salaries) for _ in range(1000)])
    df_dp = pl.DataFrame({'DP_Mean': dp_overall_mean_})

    hist_dp = alt.Chart(df_dp).mark_bar().encode(
        alt.X('DP_Mean', bin=alt.Bin(maxbins=100), title='保護後的年薪平均數'),
        y='count()'
    )

    rule = alt.Chart().mark_rule(color='red').encode(
        x=alt.X(datum=overall_mean),
        size=alt.value(3)
    )

    annot = alt.Chart().mark_text(
        text='年薪平均數',
        color='red',
        align='left',
        baseline='middle',
        dx=7
    ).encode(
        x=alt.X(datum=overall_mean),
        y=alt.value(10)
    )

    plot_dp = (hist_dp + rule + annot) if button_dp_overall.value else alt.Chart().mark_text(text='請啟動差分隱私', 
                                                                                     dx=0, dy=0, size=30, color='gray')

    mo.ui.altair_chart(plot_dp, label='執行 1000 次差分隱私的年薪平均數計算結果')
    return annot, df_dp, dp_overall_mean_, hist_dp, plot_dp, rule


@app.cell
def _(mo):
    button_dp_exclude = mo.ui.run_button(label='差分隱私，啟動！', kind='success')
    return (button_dp_exclude,)


@app.cell(hide_code=True)
def _(button_dp_exclude, mo):
    mo.md(
        f'''---
        
        ### 第一位員工以外的平均年薪

        {button_dp_exclude}
        '''
    )
    return


@app.cell
def _(button_dp_exclude, dp_mean_2, np, salaries):
    overall_exclude_mean = np.mean(salaries[1:])
    dp_exclude_mean = dp_mean_2(salaries[1:]) if button_dp_exclude.value else 0
    return dp_exclude_mean, overall_exclude_mean


@app.cell
def _(dp_exclude_mean, mo, overall_exclude_mean):
    stat_mean_salaries_exclude = mo.stat(label='第一位員工以外的平均年薪', value=overall_exclude_mean, caption='萬元')
    stat_mean_salaries_exclude_dp = mo.stat(label='第一位員工以外的平均年薪（差分隱私）', value=dp_exclude_mean, caption='萬元')
    stat_mean_diff_exclude = mo.stat(label='差異', value=overall_exclude_mean-dp_exclude_mean, caption='萬元')

    mo.hstack([stat_mean_salaries_exclude, stat_mean_salaries_exclude_dp, stat_mean_diff_exclude])
    return (
        stat_mean_diff_exclude,
        stat_mean_salaries_exclude,
        stat_mean_salaries_exclude_dp,
    )


@app.cell(hide_code=True)
def _(
    alt,
    button_dp_exclude,
    dp_mean_2,
    mo,
    np,
    overall_exclude_mean,
    pl,
    salaries,
):
    dp_exclude_mean_ = np.array([dp_mean_2(salaries[1:]) for _ in range(1000)])
    df_dp_exclude = pl.DataFrame({'DP_Mean': dp_exclude_mean_})

    hist_dp_exclude = alt.Chart(df_dp_exclude).mark_bar().encode(
        alt.X('DP_Mean', bin=alt.Bin(maxbins=100), title='保護後的第一位員工之外的年薪平均數'),
        y='count()'
    )

    rule_exclude = alt.Chart().mark_rule(color='red').encode(
        x=alt.X(datum=overall_exclude_mean),
        size=alt.value(3)
    )

    annot_exclude = alt.Chart().mark_text(
        text='第一位員工之外的年薪平均數',
        color='red',
        align='left',
        baseline='middle',
        dx=7
    ).encode(
        x=alt.X(datum=overall_exclude_mean),
        y=alt.value(10)
    )

    plot_dp_exclude = (hist_dp_exclude + rule_exclude + annot_exclude) if button_dp_exclude.value else alt.Chart().mark_text(text='請啟動差分隱私', dx=0, dy=0, size=30, color='gray')

    mo.ui.altair_chart(plot_dp_exclude, label='執行 1000 次差分隱私的年薪平均數計算結果')
    return (
        annot_exclude,
        df_dp_exclude,
        dp_exclude_mean_,
        hist_dp_exclude,
        plot_dp_exclude,
        rule_exclude,
    )


@app.cell
def _(mo):
    button_attack = mo.ui.run_button(label='差異攻擊！', kind='danger')
    return (button_attack,)


@app.cell(hide_code=True)
def _(button_attack, mo):
    mo.md(
        f"""---
        
        ### 第一位員工的年薪

        加入差分隱私後，可以看到經過差分隱私保護的年薪平均數依然與原始平均數相近，那此時我們採取差異攻擊會得到什麼結果呢？差分隱私是否可以保護第一位員工的年薪資訊不被洩露？

        {button_attack}
        """
    )
    return


@app.cell
def _(button_attack, dp_mean_1, dp_mean_2, n_obs, salaries):
    attack_income = (dp_mean_1(salaries) * n_obs - dp_mean_2(salaries[1:]) * (n_obs - 1)) if button_attack.value else 0
    return (attack_income,)


@app.cell
def _(attack_income, mo, salaries):
    stat_mean_salaries_attack = mo.stat(label='第一位員工的實際薪資', value=salaries[0], caption='萬元')
    stat_mean_salaries_attack_dp = mo.stat(label='加入差分隱私後，推測的第一位員工的薪資', value=attack_income, caption='萬元')
    stat_mean_diff_attack = mo.stat(label='差異', value=salaries[0]-attack_income, caption='萬元')

    mo.hstack([stat_mean_salaries_attack, stat_mean_salaries_attack_dp, stat_mean_diff_attack])
    return (
        stat_mean_diff_attack,
        stat_mean_salaries_attack,
        stat_mean_salaries_attack_dp,
    )


@app.cell
def _(
    alt,
    button_attack,
    dp_mean_1,
    dp_mean_2,
    mo,
    n_obs,
    np,
    pl,
    salaries,
):
    dp_overall_mean_attack_ = np.array([dp_mean_1(salaries) for _ in range(1000)])
    dp_exclude_mean_attack_ = np.array([dp_mean_2(salaries[1:]) for _ in range(1000)])
    attack_income_ = dp_overall_mean_attack_ * n_obs - dp_exclude_mean_attack_ * (n_obs - 1)
    df_attack = pl.DataFrame({'Attack Income': attack_income_})

    hist_dp_attack = alt.Chart(df_attack).mark_bar().encode(
        alt.X('Attack Income', bin=alt.Bin(maxbins=100), title='第一位員工的薪水'),
        y='count()'
    )

    rule_attack = alt.Chart().mark_rule(color='red').encode(
        x=alt.X(datum=salaries[0]),
        size=alt.value(3)
    )

    annot_attack = alt.Chart().mark_text(
        text='第一位員工的真實薪水',
        color='red',
        align='left',
        baseline='middle',
        dx=7
    ).encode(
        x=alt.X(datum=salaries[0]),
        y=alt.value(10)
    )

    plot_attack = (hist_dp_attack + rule_attack + annot_attack) if button_attack.value else alt.Chart().mark_text(text='請進行差異攻擊', dx=0, dy=0, size=30, color='gray')

    mo.ui.altair_chart(plot_attack, label='執行 1000 次差異攻擊的計算結果')
    return (
        annot_attack,
        attack_income_,
        df_attack,
        dp_exclude_mean_attack_,
        dp_overall_mean_attack_,
        hist_dp_attack,
        plot_attack,
        rule_attack,
    )


@app.cell
def _():
    import numpy as np
    import polars as pl
    import warnings
    import opendp.prelude as dp
    import altair as alt
    import marimo as mo
    from drawdata import BarWidget

    dp.enable_features('contrib')

    # hide warning created by outstanding scipy.stats issue
    warnings.simplefilter(action='ignore', category=FutureWarning)
    return BarWidget, alt, dp, mo, np, pl, warnings


if __name__ == "__main__":
    app.run()
