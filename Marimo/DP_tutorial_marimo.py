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

    請設定 20 位員工的年薪。橫軸為員工編號，從 0 開始到 19，共 20 位員工。縱軸則為每位員工對應的年薪，單位為萬元。

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
def _(mo, np, salaries):
    def service(multiselect):
        """
        顯示選擇的員工的平均年薪

        Args:
        multiselect: object 選擇器物件

        Returns:
        None
        """
        if len(multiselect.value) < 5:
            return mo.md('請選擇五位以上的員工編號')
        else:
            ind = np.array(multiselect.value, dtype='int')
            return mo.md(f'這些員工的平均年薪為 {np.mean(salaries[ind]):.2f} 萬元')
    return (service,)


@app.cell
def _(mo, multiselect, service):
    mo.callout(mo.vstack([mo.hstack([multiselect, mo.md(f'您已選擇：{multiselect.value}')]),
                         mo.md(f'''{service(multiselect)}''')]))
    return


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

        如果我們想安全地提供這項平均數計算服務，維持一樣的彈性與功能，並且**無法從輸出（平均數）來反推相關資訊**，我們可以使用差分隱私來達成。在詳細介紹以前，我們先來看看差分隱私可以做到什麼。

        在前面的實驗中，我們成功得知第一位員工的年薪。現在我們**使用差分隱私來保護平均數的計算過程**，觀察是否能有效抵禦攻擊。
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


@app.cell(hide_code=True)
def _(mo):
    mo.md("""我們可以發現，差分隱私有效地保護了資料隱私，即使攻擊者進行差異攻擊，也無法得知真實值，有時甚至會給出差異很大的答案。從上述執行 1000 次差分隱私的計算結果可發現，每次差分隱私機制輸出的值並不固定，可能會很接近真實值，也可能會遠離真實值，因此攻擊者並沒有辦法單就數次的查詢得知真實值，最多僅能「趨近」真實值。這代表差分隱私是一個有效的隱私保護機制，能夠在保護個人隱私的同時，提供有限的統計查詢功能。""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ---
        ## 原理介紹

        在前面的實驗中，我們了解到直接釋出平均數是不安全的，可能會遭受差異攻擊而能還原出個人隱私資料。並且我們也了解到：差分隱私可以防禦此攻擊，藉由加入雜訊讓攻擊者無法從輸出（平均數）來反推相關資訊，但又能給予幾乎正確的統計值查詢。差分隱私是如何做到的？接下來，我們將詳細探討差分隱私的原理。

        簡單來說，差分隱私是透過加入特定「雜訊」的方式，達成數學上可量化的隱私保護。什麼是「數學上可量化的隱私保護」呢？我們可以從差分隱私較直白的定義著手：在給定的兩個相鄰的資料集，針對分析者欲計算的目標，兩資料集所得之值形成的分配，距離不會大到讓分析者可以判斷這兩資料集有差異。

        我們接著來詳細說明

        * 什麼是相鄰的資料集
        * 什麼是分配的差異
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### 相鄰資料集/資料集距離

        相鄰的定義為兩資料集只差一個個體的記錄，一般來說這代表資料集的距離為 1，不過如何何謂「資料集的距離」？這邊我們採用 Symmetric Distance 進行定義，也就是兩個資料集的差集大小。換個方式說，這個值代表在取出一個個體記錄後，這兩個資料集相差幾筆資料。若寫成數學的形式：

        $$d_{Sym}(u,v) = |u-v ∪ v-u| = \sum_{x}|\#\{i:x=u_i\}-\#\{i:x=v_i\}|$$

        其中 $u,v$ 為兩個資料集。舉例來說，若 $u=\{1,2,3\}, v=\{1,2\}$，則 $d_{Sym}(u,v)=1.$

        需要注意的是，有些時候相鄰的資料集距離並非距離為 1。例如若每一個客戶在資料集中與 5 筆記錄有關，則此時距離為 5。不過在差分隱私中，我們基本上都預設一個個體在資料集中的記錄只有一筆，以簡化計算。

        ### 分配的差異 (Divergence)

        在統計上，有多種方式可以定義兩個分配之間的距離，在此我們採用的是 Max Divergence，代表在所有可能的範圍內，兩個分配最大的差異。下圖代表的是給定一個範圍 (支撐集/support) $S$，兩個分配的差異圖：

        ![](https://docs.opendp.org/en/stable/_images/theory_a-framework-to-understand-dp_11_0.png)

        Pic. from OpenDP

        其中藍底、橘底的部分分別代表兩分配（以藍色線、橘色線表示）在給定範圍 $S$ 下的差異。具體計算方法如下：

        $$D_{\text{MaxDivergence}}(M(u),M(v))=\max_{S\subseteq\text{supp}(M(u))}\log(\frac{\text{Pr}[M(u)\in S]}{\text{Pr}[M(v)\in S]})$$

        以上圖的例子，可以將藍底、橘底的面積相除，取 log，即可得到針對此 $S$ 的 Divergence。而我們所求的，即是透過改變 $S$，找出最大的 $\log(\frac{\text{Pr}[M(u)\in S]}{\text{Pr}[M(v)\in S]}).$

        > 為何需要定義分配的差異？
        > 
        > 因為差分隱私的結果為一服從特定分配的隨機變數，因此需要從分配的角度去測量差分隱私結果。如上圖所示，若藍線代表原始資料加入差分隱私後，所形成的分配；而橘線則是相鄰資料集加入差分隱私後，所形成的分配。因此兩者之間的差異越大，分析者越能發現兩者之間的差異，讓分析者能夠區分出這個結果是否為真實值；相反的，若 Divergence 越小，則分析者則越難判斷這個結果是否為真實值，藉此保證個人隱私不會被洩漏。

        ### 敏感度 (Sensitivity)

        一般來說，在計算差分隱私是計算一統計量的值，例如：總和、平均數等等。但是當我們移除/新增一筆資料（相鄰資料集距離為 1），會改變這些統計量的計算結果，這會進一步影響到計算分配差異的結果。舉例來說，若移除/新增一筆資料會導致統計量計算結果大幅變動，Divergence 也會有大幅的變動。因此兩資料集所得之值形成的分配，可接受的距離可以更大，而分析者仍無法判斷這兩資料集有差異。換句話說，在可接受距離更大的情況下，我們可以在資料集內加入更多雜訊，而不會讓分析者有辦法判斷這兩資料集有差異。而移除/新增一筆資料，導致統計量計算結果的最大改變量，即為敏感度。

        在敏感度的計算上，我們採用 Absolute Distance，定義如下：

        $$d_{Abs}(a,b) = |a-b|$$

        舉例來說，以考試成績為例，滿分為 100 分的狀況下，移除/新增一位學生的成績，會導致總分的變化至多 100 分，因此在此案例中，進行總分計算的敏感度為 100。但如果我們只是想要了解資料集中究竟包含幾位同學的成績，則移除/新增一位同學的成績至多只會讓我們的查詢結果改變 1，因此進行計數的敏感度為 1。

        然而在很多現實狀況下，敏感度沒有那麼容易定義，因為資料集本身並沒有明顯的上下界，例如薪資。這會導致 Divergence 變得無限大，需要加入的雜訊為無限多。為了避免這種情形，我們會限制上下界，稱之為 clamping/clipping，藉此來控制敏感度大小。例如將薪資限制在 1000 萬，超過 1000 萬的值都會被調整為 1000 萬。

        常見統計量計算的敏感度：

        * 計數：1
        * 總和：資料取絕對值後的最大值
        * 平均：$(U-L)/n$，其中 $U,L$ 分別代表資料最大值、最小值，$n$ 為資料集總筆數

        ### 差分隱私（嚴謹的定義）

        當我們了解資料集距離、分配的差異後，我們可以對（差分）隱私進行明確的定義：

        > 若一個隱私演算法 $M(\cdot)$ 在給定資料集距離為 $k$ 時，任何資料集組合 $u,v$ 滿足 $d_{Sym}(u,v)\le k$，都滿足 $D_{\text{MaxDivergence}}(M(u),M(v))\le\epsilon$，則 $M(\cdot)$ 為 $\epsilon$-差分隱私。

        這等價於另一學術上常見的定義：

        > 若一個隱私演算法 $M(\cdot)$ 在相鄰資料集中的任何資料集組合 $u,v$ 都滿足 $\text{Pr}(M(u)\in S)\le e^\epsilon\cdot\text{Pr}(M(u)\in S)$，則 $M(\cdot)$ 為 $\epsilon$-差分隱私。

        ### 概念彙整

        至此我們介紹完差分隱私重要的幾個元素，接下來將會利用這些元素進行組合，進行差分隱私的計算。理論上，進行差分隱私的計算時，我們會需要先計算相鄰資料集的距離，接著進行上下界的調整，以確保接下來進行敏感度計算上是有限的 (bounded)。接著再進行統計值的計算，如計數、平均數、總合等。計算過程中，我們可以藉由比較相鄰資料集經過統計值計算後的結果，得知敏感度與分配差異，藉此得知要加入多少雜訊來保護資料（或者藉由加入的雜訊量得知隱私保護力 $\epsilon$）。

        數學上，若我們將相鄰的兩資料集 ($X,Y$) 之距離以 Symmetric Distance 計算，並以 $d_{in}$ 來表示（即 $d_{Sym} = d_{in}$），則經過上下界調整後（調整至 $[L,U]$），我們可以確保進行總和運算後，敏感度為：

        $$\Delta=\max|\text{clamped sum}(X)-\text{clamped sum}(Y)|=d_{in}\cdot\max(|L|,U)$$

        接著我們將總和運算結果分別以 $x,y$ 表示，並利用一 $\epsilon$-差分隱私演算法：拉普拉斯機制 (Laplace Mechanism) $M$ 加入雜訊，其中拉普拉斯機制需要給定一參數 scale，我們將其設為 $b$，則對於 $x,y\in\mathbb{R}$ 使得 $d_{Abs}(x,y)\leq \Delta$ 且 $d_{out}=\Delta/b$，分配差異為：

        $$D_{\text{MaxDivergence}}(M(x),M(y))\le d_{out}$$

        而 $d_{out}$ 即為 $\epsilon$，兩者等價。

        因此，在整個資料流程中，首先要決定 $d_{in}$ 的計算方式，接著進行資料處理，例如 clamping 來限制敏感度。接著在差分隱私演算法中，則根據我們選定的敏感度計算方法計算出 $\Delta$，並利用選定的分配差異計算方式來求得在給定的 $\epsilon$ $(d_{out})$ 下，應加入多少雜訊。

        下列項目為執行差分隱私演算法時，需考慮的元素以及在本範例中使用的方法：

        * 資料集之間的距離：Symmetric Distance
        * 分配的差異：Max Divergence
        * 敏感度：Absolute Distance

        ### $\epsilon$ 在拉普拉斯機制 (Laplace Mechanism) 中的應用

        在現實生活中，常常看到不同的論文或技術提到其採用特定 $\epsilon$ 的差分隱私，究竟 $\epsilon$ 對結果會有什麼影響呢？我們以一個常見的差分隱私機制——拉普拉斯機制為例，來說明 $\epsilon$ 如何影響結果。

        拉普拉斯機制 $M$ 加雜訊的方式如下：

        $$M(x)=x+\text{Lap}(\frac{\Delta}{\epsilon})$$

        其中 $x$ 為統計值，$\frac{\Delta}{\epsilon}$ 為拉普拉斯機制所需參數 scale，在此我們以 $b$ 表示，而 $\text{Lap}$ 則為拉普拉斯分配，其機率密度函數如下：

        <p><img src="https://upload.wikimedia.org/wikipedia/commons/0/0a/Laplace_pdf_mod.svg" alt="Probability density plots of Laplace distributions" height="300" width="400"><br>By <a href="//commons.wikimedia.org/wiki/User:IkamusumeFan" title="User:IkamusumeFan">IkamusumeFan</a> - <span class="int-own-work" lang="en">Own work</span>, <a href="https://creativecommons.org/licenses/by-sa/4.0" title="Creative Commons Attribution-Share Alike 4.0">CC BY-SA 4.0</a>, <a href="https://commons.wikimedia.org/w/index.php?curid=34776178">Link</a></p>

        scale 即為圖中的參數 b。

        由公式可知：

        $$b = \frac{\Delta}{\epsilon}$$

        其中根據定義，$\epsilon=d_{out}$（兩者等價），因此可推得：

        $$\epsilon=d_{out}=\frac{\Delta}{b}$$

        即為上一節的計算過程。

        從這邊我們可以得知，在不改變 $\Delta$ 的情況下，改變 $\epsilon$ 會改變 $b$ 的值。那們改變 $b$ 對於加入的雜訊量會有什麼影響呢？我們可以藉由下方的範例來觀察。
        """
    )
    return


@app.cell
def _(mo):
    slider_lp = mo.ui.slider(start=1, stop=10, step=0.5, value=1, label='拉普拉斯機制的 scale 參數 b')
    return (slider_lp,)


@app.cell
def _(np, pl, slider_lp):
    rng = np.random.default_rng(seed=0)
    lp_samples = rng.laplace(0, slider_lp.value, 1000)
    df_lp = pl.DataFrame({'Data': lp_samples})
    return df_lp, lp_samples, rng


@app.cell
def _(alt, df_lp, slider_lp):
    hist_lp = alt.Chart(df_lp).mark_bar().encode(
        alt.X('Data', bin=alt.Bin(maxbins=100), title=f'拉普拉斯機制的 scale 參數 b = {slider_lp.value}'),
        y='count()'
    )
    return (hist_lp,)


@app.cell
def _(hist_lp, mo, slider_lp):
    mo.vstack([mo.hstack([slider_lp, mo.md(f'目前的 b 為：{slider_lp.value}')]), mo.ui.altair_chart(hist_lp, label='拉普拉斯機制的雜訊分配')])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""由圖可知，若將 $b$ 增大，會導致值往兩側擴散，大部分的值會更加偏離 0，導致加入的雜訊量較多。將前面我們已知的 $\epsilon$ 與 $b$ 的關係連結起來，便能推出：$\epsilon$ 越小，會加入的雜訊量越多。加入的雜訊越多越能混淆分析後的結果，讓攻擊者更難推論出正確的值，因此保護力提升。反之，若 $\epsilon$ 越大，則加入的雜訊量越少，分析後的結果會更接近真實值，但也會讓攻擊者更容易推論出正確的值，因此保護力下降。""")
    return


@app.cell
def _(mo):
    button_eps = mo.ui.run_button(kind='success', label='差分隱私，啟動！', full_width=True)
    slider_eps = mo.ui.slider(start=1.0, stop=20.0, step=0.5, value=10.0, label='epsilon')
    return button_eps, slider_eps


@app.cell
def _(make_dp_mean, n_obs, slider_eps):
    dp_mean_eps_1 = make_dp_mean((0.0, 200.0),n_obs,slider_eps.value)
    dp_mean_eps_2 = make_dp_mean((0.0, 200.0),n_obs-1,slider_eps.value)
    return dp_mean_eps_1, dp_mean_eps_2


@app.cell
def _(button_eps, dp_mean_eps_1, salaries):
    dp_overall_mean_eps = dp_mean_eps_1(salaries) if button_eps.value else 0
    return (dp_overall_mean_eps,)


@app.cell
def _(button_eps, dp_mean_eps_2, salaries):
    dp_exclude_mean_eps = dp_mean_eps_2(salaries[1:]) if button_eps.value else 0
    return (dp_exclude_mean_eps,)


@app.cell
def _(button_eps, dp_mean_eps_1, dp_mean_eps_2, n_obs, salaries):
    attack_income_eps = (dp_mean_eps_1(salaries) * n_obs - dp_mean_eps_2(salaries[1:]) * (n_obs - 1)) if button_eps.value else 0
    return (attack_income_eps,)


@app.cell
def _(dp_overall_mean_eps, mo, overall_mean):
    stat_mean_salaries_eps = mo.stat(label='所有員工的平均年薪', value=overall_mean, caption='萬元')
    stat_mean_salaries_eps_dp = mo.stat(label='所有員工的平均年薪（差分隱私）', value=dp_overall_mean_eps, caption='萬元')
    stat_mean_eps_diff = mo.stat(label='差異', value=overall_mean-dp_overall_mean_eps, caption='萬元')
    return (
        stat_mean_eps_diff,
        stat_mean_salaries_eps,
        stat_mean_salaries_eps_dp,
    )


@app.cell
def _(dp_exclude_mean_eps, mo, overall_exclude_mean):
    stat_mean_salaries_exclude_eps = mo.stat(label='第一位員工以外的平均年薪', value=overall_exclude_mean, caption='萬元')
    stat_mean_salaries_exclude_eps_dp = mo.stat(label='第一位員工以外的平均年薪（差分隱私）', value=dp_exclude_mean_eps, caption='萬元')
    stat_mean_diff_exclude_eps = mo.stat(label='差異', value=overall_exclude_mean-dp_exclude_mean_eps, caption='萬元')
    return (
        stat_mean_diff_exclude_eps,
        stat_mean_salaries_exclude_eps,
        stat_mean_salaries_exclude_eps_dp,
    )


@app.cell
def _(attack_income_eps, mo, salaries):
    stat_mean_salaries_attack_eps = mo.stat(label='第一位員工的實際薪資', value=salaries[0], caption='萬元')
    stat_mean_salaries_attack_eps_dp = mo.stat(label='加入差分隱私後，推測的第一位員工的薪資', value=attack_income_eps, caption='萬元')
    stat_mean_diff_attack_eps = mo.stat(label='差異', value=salaries[0]-attack_income_eps, caption='萬元')
    return (
        stat_mean_diff_attack_eps,
        stat_mean_salaries_attack_eps,
        stat_mean_salaries_attack_eps_dp,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(f'''---

    ## $\epsilon$ 對於差分隱私的影響

    最後，讓我們回到最一開始的 20 人年薪資料，看看我們如何透過調整不同大小的 $\epsilon$ 來保護第一位員工的年薪資料。
    ''')
    return


@app.cell
def _(
    alt,
    button_eps,
    dp_mean_eps_1,
    dp_mean_eps_2,
    n_obs,
    np,
    pl,
    salaries,
):
    dp_overall_mean_attack_eps_ = np.array([dp_mean_eps_1(salaries) for _ in range(1000)])
    dp_exclude_mean_attack_eps_ = np.array([dp_mean_eps_2(salaries[1:]) for _ in range(1000)])
    attack_income_eps_ = dp_overall_mean_attack_eps_ * n_obs - dp_exclude_mean_attack_eps_ * (n_obs - 1)
    df_attack_eps = pl.DataFrame({'Attack Income': attack_income_eps_})

    hist_dp_attack_eps = alt.Chart(df_attack_eps).mark_bar().encode(
        alt.X('Attack Income', bin=alt.Bin(maxbins=100), title='第一位員工的薪水'),
        y='count()'
    )

    rule_attack_eps = alt.Chart().mark_rule(color='red').encode(
        x=alt.X(datum=salaries[0]),
        size=alt.value(3)
    )

    annot_attack_eps = alt.Chart().mark_text(
        text='第一位員工的真實薪水',
        color='red',
        align='left',
        baseline='middle',
        dx=7
    ).encode(
        x=alt.X(datum=salaries[0]),
        y=alt.value(10)
    )

    plot_attack_eps = (hist_dp_attack_eps + rule_attack_eps + annot_attack_eps) if button_eps.value else alt.Chart().mark_text(text='請啟動差分隱私', dx=0, dy=0, size=30, color='gray')
    return (
        annot_attack_eps,
        attack_income_eps_,
        df_attack_eps,
        dp_exclude_mean_attack_eps_,
        dp_overall_mean_attack_eps_,
        hist_dp_attack_eps,
        plot_attack_eps,
        rule_attack_eps,
    )


@app.cell
def _(
    button_eps,
    mo,
    plot_attack_eps,
    slider_eps,
    stat_mean_diff_attack_eps,
    stat_mean_diff_exclude_eps,
    stat_mean_eps_diff,
    stat_mean_salaries_attack_eps,
    stat_mean_salaries_attack_eps_dp,
    stat_mean_salaries_eps,
    stat_mean_salaries_eps_dp,
    stat_mean_salaries_exclude_eps,
    stat_mean_salaries_exclude_eps_dp,
):
    mo.vstack([
        mo.hstack([slider_eps, mo.md(f'目前的 epsilon 為：{slider_eps.value}')], justify='space-around'),
        mo.hstack([button_eps], justify='center'),
        mo.md('''---'''),
        mo.hstack([mo.vstack([mo.md(r'''$\quad$ 實際資料'''), stat_mean_salaries_eps, 
                              stat_mean_salaries_exclude_eps, stat_mean_salaries_attack_eps]),
                  mo.vstack([mo.md(r'''$\quad$ 透過差分隱私計算的結果'''), stat_mean_salaries_eps_dp, 
                             stat_mean_salaries_exclude_eps_dp, stat_mean_salaries_attack_eps_dp]),
                  mo.vstack([mo.md(r'''$\quad$ 兩者差異'''), stat_mean_eps_diff, 
                             stat_mean_diff_exclude_eps, stat_mean_diff_attack_eps])]),
        mo.ui.altair_chart(plot_attack_eps, label='執行 1000 次差異攻擊的計算結果')
    ])
    return


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


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
