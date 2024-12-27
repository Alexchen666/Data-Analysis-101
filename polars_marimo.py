import marimo

__generated_with = "0.10.7"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Data Analysis 101 - Polars

        Alex Chen

        Source:

        https://github.com/allisonhorst/palmerpenguins/tree/main

        https://www.kaggle.com/datasets/parulpandey/palmer-archipelago-antarctica-penguin-data

        Gorman KB, Williams TD, Fraser WR (2014). Ecological sexual dimorphism and environmental variability within a community of Antarctic penguins (genus Pygoscelis). PLoS ONE 9(3):e90081. https://doi.org/10.1371/journal.pone.0090081

        ---

        在此教學中，我們會利用一公開資料集來進行基礎的資料分析。這個資料集是一個關於三種企鵝的觀察資料。

        本文共分為九個段落，分別對應到資料處理過程中常見的九種情境。透過這份教學，預期你可以學會如何使用近期 Python 上熱門的資料分析套件 `polars` 進行資料處理，以解決常見的實務問題。

        接下來，就開始我們的資料分析之旅！

        ![Penguins](https://github.com/allisonhorst/palmerpenguins/blob/main/man/figures/lter_penguins.png?raw=true)

        Artwork by @allison_horst
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        首先，我們需要匯入此專案中需要的套件：

        * `polars`: 資料處理
        * `pandas`: 內含 Python 常見的資料表型態
        * `matplotlib`: 資料視覺化
        * `seaborn`: 資料視覺化（進階）

        在下方程式碼中，`as` 是用來幫套件取別稱。如此一來，在接下來的程式碼中，若需要用到套件時，就不需要輸入全名，例如需要用到 `pandas` 時，只需要輸入 `pd` 就可以了。
        """
    )
    return


@app.cell
def _():
    import polars as pl
    import matplotlib.pyplot as plt
    import seaborn as sns

    plt.style.use('seaborn-v0_8-darkgrid')
    return pl, plt, sns


@app.cell
def _(mo):
    mo.md(r"""下方程式碼是如果需要在視覺化中加入中文時，需要使用的額外控制。""")
    return


@app.cell
def _(plt):
    import matplotlib.font_manager as fm
    fm.fontManager.addfont('Supplements/NotoSansTC-VariableFont_wght.ttf')
    plt.rcParams['font.sans-serif'] =  ['Noto Sans TC']
    plt.rcParams['axes.unicode_minus']=False # 用來正常顯示負號
    return (fm,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        `polars` 與其他資料處理套件之間最大的區別，在於它引入了 lazy mode 的概念，可以針對資料處理流程進行最佳化，讓執行效率大幅提升。為了達到這點，`polars` 在語法上與其他套件有差異，並提升了可讀性。

        在 `polars` 中，語法大致上可被分為兩類：Expression 與 Context。Expression 是資料處理、轉換過程中的表達式，表達「你想對資料做什麼處理」。表達式的運用很彈性且模組化，就像積木一樣，可以用簡單的表達式組合出複雜的資料處理流程。Expression 本身是惰性運算的 (lazy computation)，也就是說當輸入 Expression 後，並沒有任何運算實際執行。要實際執行這些運算，需要透過 Context。Context 代表的是執行的情境，也就是「你想要怎麼執行這些表達式」。常見的 Context 有四種：`select`（只會輸出選取的欄位）, `with_columns`（輸出原始的資料表加上進行運算的欄位）, `filter`（篩選）, `group_by`（聚合）。這些 Context 需與 Expression 搭配使用，才能實際執行。在此過程中 `polars` 會根據 Expression 的內容設計有效率的執行方式，以提升執行速度。
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # 1. 讀入資料

        在進行資料分析前，最一開始一定要把資料讀取到執行環境中，才可以發揮套件的功能。`polars` 支援所有常見的資料格式，包括 `.csv`, `.xlsx` 等。

        將套件讀入後，我們需要將資料存放在一個「變數」內，之後我們就可以藉由這個變數來對資料進行處理。這個變數的格式，我們稱之為資料表 (dataframe)。

        > `polars` 讀取 `.xlsx` 檔案需要 `fastexcel` 套件。
        """
    )
    return


@app.cell
def _(pl):
    df1 = pl.read_csv('Tutorial_Data/penguins_info.csv')
    return (df1,)


@app.cell
def _(pl):
    df2 = pl.read_excel('Tutorial_Data/penguins_measurements.xlsx')
    return (df2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # 2. 資料概覽

        讀入資料後，我們來看一看讀入的資料究竟長什麼樣子，以及藉由一些語法，帶我們了解資料集的樣態。
        """
    )
    return


@app.cell
def _(df1):
    df1 # 直接輸入 df1 可檢視資料
    return


@app.cell
def _(df1):
    df1.head() # 顯示前五筆資料
    return


@app.cell
def _(df1):
    df1.shape # 顯示資料筆數與欄位數
    return


@app.cell
def _(df1):
    df1.columns # 顯示欄位名稱
    return


@app.cell
def _(df1):
    df1.describe() # 數值型資料的描述性統計
    return


@app.cell
def _(df1):
    df1.schema # 欄位的資料型態
    return


@app.cell
def _(df1, pl):
    df1.select(pl.col('Species').value_counts()).unnest('Species') # 類別型資料的計數
    return


@app.cell
def _(df2):
    df2.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""![Culmen](https://github.com/allisonhorst/palmerpenguins/blob/main/man/figures/culmen_depth.png?raw=true)""")
    return


@app.cell
def _(df2):
    df2.schema
    return


@app.cell
def _(df2, pl):
    df2.select(pl.col('Body Mass (g)').min()) # 最小值
    return


@app.cell
def _(df2, pl):
    df2.select(pl.col('Body Mass (g)').max()) # 最大值
    return


@app.cell
def _(df2, pl):
    df2.select(pl.col('Body Mass (g)').mean()) # 平均值
    return


@app.cell
def _(df2, pl):
    df2.select(pl.col('Body Mass (g)').std()) # 標準差
    return


@app.cell
def _(df2, pl):
    df2.select(pl.col('Body Mass (g)').median()) # 中位數
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # 3. 資料搜索

        對資料有粗淺的了解後，我們可以利用一些語法搜索特定資料，將焦點放在我們感興趣的資料上。
        """
    )
    return


@app.cell
def _(df2, pl):
    df2.select(pl.col('Culmen Depth (mm)')) # 透過 select, pl.col 取得欄位資料
    return


@app.cell
def _(df2, pl):
    df2.select(pl.col('Culmen Depth (mm)', 'Body Mass (g)')) # 用同樣方式取得多個欄位資料
    return


@app.cell
def _(df2, pl):
    df2.select(pl.col('Culmen Depth (mm)').gather(1)) # 取得特定列與欄的資料，先利用 pl.col 取得欄位，再用 gather 取得列
    return


@app.cell
def _(df2, pl):
    df2.select(pl.col('Culmen Depth (mm)', 'Body Mass (g)').gather(1)) # 取得特定列與多個欄的資料
    return


@app.cell
def _(df2, pl):
    df2.select(pl.col('Culmen Depth (mm)', 'Body Mass (g)').gather([1, 4])) # 取得多列與多欄的資料
    return


@app.cell
def _(df2, pl):
    # 取得符合條件的列與欄的資料
    # 在此代表我們要取得 'Body Mass (g)' 大於等於 6000 的列，並且取得 'Culmen Depth (mm)' 與 'Body Mass (g)' 欄的資料
    df2.filter(pl.col('Body Mass (g)') >= 6000).select(pl.col('Culmen Depth (mm)', 'Body Mass (g)'))
    return


@app.cell
def _(mo):
    mo.md(r"""常見的條件運算符包含：`==`（等於）, `>`（大於）, `<`（小於）, `>=`（大於等於）, `<=`（小於等於）, `!=`（不等於）。""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # 4. 資料清理與修改

        選取資料後，會發現資料中有需要調整的地方，例如某些值有誤，或者是某些欄位不需要，也有可能是有缺失值（ N/A 值）需要移除。接下來我們來看看 `polars` 如何處理這些情況。
        """
    )
    return


@app.cell
def _(df2):
    df_temp = df2.drop(['Culmen Length (mm)', 'Culmen Depth (mm)']) # 刪除欄位
    return (df_temp,)


@app.cell
def _(df_temp):
    df_temp.head()
    return


@app.cell
def _(df_temp):
    df_temp[1, 'ID'] = 1 # 修改特定列與欄的資料
    df_temp[1, 'Flipper Length (mm)'] = 181
    df_temp[1, 'Body Mass (g)'] = 3750
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""> 注意！雖然在 `polars` 中可以像 `pandas` 一樣使用方括號進行選取與修改，但是其執行效率較差（`polars` 無法在 lazy mode 下進行最佳化，且無法進行平行運算）。因此使用方括號只有在方便性為最重要考量下，才使用的最後手段。事實上，在官方文件中並看不到方括號的使用方法。""")
    return


@app.cell
def _(df_temp):
    df_temp.head()
    return


@app.cell
def _(df_temp):
    df_temp.is_duplicated().sum() # 計算重複的列數
    return


@app.cell
def _(df_temp):
    df_temp2 =df_temp.unique(maintain_order=True) # 刪除重複的列
    return (df_temp2,)


@app.cell
def _(df_temp2):
    df_temp2.head()
    return


@app.cell
def _(df_temp, df_temp2):
    print('清理前資料筆數:', df_temp.shape[0], '\n清理後資料筆數:', df_temp2.shape[0])
    return


@app.cell
def _(df2, pl):
    df2.select(pl.all().is_null().any()) # 判斷是否有遺失值
    return


@app.cell
def _(df2):
    df2.null_count() # 欄位遺失值的計數
    return


@app.cell
def _(df2, pl):
    df2.filter(pl.any_horizontal(pl.all().is_null())) # 取得有遺失值的列
    return


@app.cell
def _(df2):
    df2_1 = df2.drop_nulls()
    return (df2_1,)


@app.cell
def _(df1, pl):
    df1.select(pl.all().is_null().any())
    return


@app.cell
def _(df1):
    df1.null_count()
    return


@app.cell
def _(df1):
    df1_1 = df1.drop_nulls()
    return (df1_1,)


@app.cell
def _(df1_1, pl):
    df1_1.select(pl.col('Sex').value_counts()).unnest('Sex')
    return


@app.cell
def _(df1_1, pl):
    df1_1.filter(pl.col('Sex') == '.')
    return


@app.cell
def _(df1_1, pl):
    df1_2 = df1_1.filter(~(pl.col('Sex') == '.'))
    return (df1_2,)


@app.cell
def _(df1_2, pl):
    df1_2.select(pl.col('Sex').value_counts()).unnest('Sex')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # 5. 資料合併

        有時候，合併資料才能發揮其價值，那要如何合併呢？最重要的有兩個關鍵：選定合併的鍵值（要根據哪個欄位來進行資料合併）以及合併方式（以誰為主要的合併參考對象）。決定好後，剩下的就交給 `polars`。

        ![join](https://realpython.com/cdn-cgi/image/width=811,format=auto/https://files.realpython.com/media/join_diagram.93e6ef63afbe.png)

        Image from https://realpython.com/pandas-merge-join-and-concat/
        """
    )
    return


@app.cell
def _(df1_2):
    df1_2.head()
    return


@app.cell
def _(df1_2):
    df1_2.shape
    return


@app.cell
def _(df2_1):
    df2_1.head()
    return


@app.cell
def _(df2_1):
    df2_1.shape
    return


@app.cell
def _(df1_2, df2_1):
    df_m1 = df1_2.join(df2_1, on='ID')
    return (df_m1,)


@app.cell
def _(df_m1):
    df_m1.head()
    return


@app.cell
def _(df_m1):
    df_m1.shape # inner join 會取兩個資料集的交集
    return


@app.cell
def _(df1_2, df2_1):
    df_m2 = df1_2.join(df2_1, on='ID', how='right')
    return (df_m2,)


@app.cell
def _(df_m2):
    df_m2.head()
    return


@app.cell
def _(df_m2):
    df_m2.shape # right join 會取右邊資料集的所有資料
    return


@app.cell
def _(df1_2, df2_1):
    df = df1_2.join(df2_1, on='ID')
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# 小試身手 1""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""任務 1: 讀入 `penguins_test1.csv` 資料集。""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""任務 2: 取得以下資訊：資料總筆數、欄位數、三種企鵝的數目、雌雄性個數、嘴喙寬中位數。""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""任務 3: 列出所有嘴喙寬大於等於 20 毫米的企鵝的嘴喙長與鰭長。""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""任務 4: 確保資料無遺失值及重複值後，計算所有企鵝的平均體重。""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # 6. 資料聚合

        資料聚合讓我們可以分門別類了解不同資料的特性，用簡單的方式認識資料。
        """
    )
    return


@app.cell
def _(df):
    df.head()
    return


@app.cell
def _(df, pl):
    df.group_by('Species').agg(pl.mean('Body Mass (g)')) # 透過 group_by 與 agg 計算不同企鵝的平均體重
    return


@app.cell
def _(df, pl):
    df.group_by('Species').agg(pl.mean('Body Mass (g)').alias('體重平均數'), pl.std('Body Mass (g)').alias('體重標準差')) # 透過 group_by 與 agg 計算不同企鵝的平均體重與標準差
    return


@app.cell
def _(df, pl):
    df.group_by('Species', 'Sex').agg(pl.mean('Body Mass (g)')) # 透過 groupby 與 agg 計算不同種類、不同性別企鵝的平均體重
    return


@app.cell
def _(df, pl):
    df.group_by('Species', 'Sex').agg(pl.mean('Body Mass (g)').alias('體重平均數'), 
                                      pl.std('Body Mass (g)').alias('體重標準差'),
                                      pl.mean('Culmen Length (mm)').alias('嘴喙長平均數'),
                                      pl.std('Culmen Length (mm)').alias('嘴喙長標準差')) # 透過 groupby 與 agg 計算不同種類、不同性別企鵝的體重及嘴喙長平均與標準差
    return


@app.cell
def _(df, pl):
    # 透過 groupby 與 agg 計算不同種類、不同性別企鵝的平均體重與標準差，以及其嘴喙長度最小值與最大值
    df.group_by('Species', 'Sex').agg(pl.mean('Body Mass (g)').alias('體重平均數'), 
                                      pl.std('Body Mass (g)').alias('體重標準差'),
                                      pl.min('Culmen Length (mm)').alias('嘴喙長最小值'),
                                      pl.max('Culmen Length (mm)').alias('嘴喙長最大值'))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # 7. 資料排序

        透過排序，我們能快速找出前幾大（小）的資料。此外，我們還可以根據多個欄位進行排序喔！
        """
    )
    return


@app.cell
def _(df):
    df.head()
    return


@app.cell
def _(df):
    df.sort('Body Mass (g)') # 透過 sort 針對體重排序資料，預設降冪排序
    return


@app.cell
def _(df):
    # 透過 sort 針對體重與鰭長排序資料，其中 descending=[False, True] 代表體重升冪排序，鰭長降冪排序
    df.sort(['Body Mass (g)', 'Flipper Length (mm)'], descending=[False, True])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # 8. 資料視覺化

        有時候單看表格資料是不夠的，透過有效的視覺化，能夠讓我們快速掌握資料，並更方便地將分析結果呈現給他人觀賞。

        > `polars` 內建的視覺化方法需要 `altair` 套件。
        """
    )
    return


@app.cell
def _(df):
    df.plot.point(x='Body Mass (g)', y='Flipper Length (mm)', color='Species') # 繪製散佈圖
    return


@app.cell
def _(df, pl):
    df.select(pl.col('Body Mass (g)').value_counts()).unnest('Body Mass (g)').plot.bar(x='Body Mass (g)', y='count') # 繪製長條圖
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""我們也可以利用 `matplotlib` 來繪製圖表，並加入更多客製化選項。""")
    return


@app.cell
def _(df, plt):
    plt.scatter(df['Body Mass (g)'], df['Flipper Length (mm)']) # 透過 plt.scatter 繪製散佈圖
    plt.title('體重與鰭長的散佈圖')
    return


@app.cell
def _(df, plt):
    plt.hist(df['Body Mass (g)']) # 透過 plt.hist 繪製直方圖
    plt.title('體重的直方圖')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""`seaborn` 是另一個在 Python 上常用的視覺化套件。它包含各種統計常用的視覺化工具，並以簡單的語法繪製出精細的圖表，因此廣受好評。""")
    return


@app.cell
def _(df, sns):
    _ax = sns.scatterplot(data=df, x='Body Mass (g)', y='Flipper Length (mm)', hue='Species')
    sns.move_legend(_ax, 'upper left', bbox_to_anchor=(1, 1))
    return


@app.cell
def _(df, sns):
    _ax = sns.histplot(data=df, x='Body Mass (g)', hue='Species', kde=True, bins=20)
    sns.move_legend(_ax, 'upper left', bbox_to_anchor=(1, 1))
    return


@app.cell
def _(df, plt, sns):
    _ax = sns.countplot(data=df, x='Species', hue='Sex')
    sns.move_legend(_ax, 'upper left', bbox_to_anchor=(1, 1))
    plt.xticks(rotation=45)
    return


@app.cell
def _(df, plt, sns):
    _ax = sns.boxplot(data=df, x='Species', y='Body Mass (g)')
    plt.xticks(rotation=45)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # 9. 資料匯出

        當資料處理完成後，我們可以將其匯出，供其他人使用。
        """
    )
    return


@app.cell
def _():
    # df.write_csv('final_penguins_pl.csv') # 將資料輸出成 CSV 檔，並且不輸出索引
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""> `polars` 需要 `xlsxwriter` 套件才能輸出 Excel 檔。""")
    return


@app.cell
def _():
    # df.write_excel('final_penguins_pl.xlsx') # 將資料輸出成 Excel 檔，並且不輸出索引
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# 小試身手 2""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""任務 1: 讀入 `penguins_test2_1.csv` 與 `penguins_test2_2.csv` 資料集。""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""任務 2: 確認兩資料集的描述性統計與資料筆數、欄位數目，以及是否有重複值、遺失值。""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""任務 3: 將兩資料集依據 `ID` 欄位合併，僅合併兩資料集共有的 `ID` 部分。""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""任務 4: 計算不同島嶼上，不同企鵝種類下，不同性別的平均體重與鰭長中位數。""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""任務 5: 根據嘴喙長再根據嘴喙寬進行排序，其中嘴喙長請用降冪排序、嘴喙寬請用升冪排序。""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""任務 6: 繪製不同企鵝種類（以顏色區分）的嘴喙長與嘴喙寬的散布圖。""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # 恭喜完成 Data Analysis 101 - Polars 的課程

        透過這份教學，你已經了解基本的 `polars` 使用方法。如果想要學習更多的話，可以到 [polars 官網](https://docs.pola.rs/api/python/stable/reference/index.html) 學習更多指令的用法 :)

        如果是熟悉 `pandas` 的使用者，則可以參考這兩份資源：[Modern Polars](https://kevinheavey.github.io/modern-polars/), [Cheatsheet for Pandas to Polars](https://www.rhosignal.com/posts/polars-pandas-cheatsheet/)
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
