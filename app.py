import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.tsa.api as smt
import streamlit as st
# from sktime.performance_metrics.forecasting import smape_loss
# from sktime.utils.plotting.forecasting import plot_ys
from sktime.forecasting.all import plot_series
from sktime.forecasting.arima import AutoARIMA
# sktime models
from sktime.forecasting.model_selection import temporal_train_test_split
from pmdarima import auto_arima

warnings.filterwarnings('ignore')

st.title('Time Series - ML')


@st.cache
def tsplot(y, lags=None, figsize=(20, 12), style='bmh'):
    """
        Plot time series, its ACF and PACF

        y - timeseries
        lags - how many lags to include in ACF, PACF calculation
    """

    with plt.style.context(style):
        fig = plt.figure(figsize=figsize)
        layout = (2, 2)
        ts_ax = plt.subplot2grid(layout, (0, 0), colspan=2)
        acf_ax = plt.subplot2grid(layout, (1, 0))
        pacf_ax = plt.subplot2grid(layout, (1, 1))

        y.plot(ax=ts_ax)
        smt.graphics.plot_acf(y, lags=lags, ax=acf_ax)
        smt.graphics.plot_pacf(y, lags=lags, ax=pacf_ax)
        plt.tight_layout()


def null_values(df):
    null_test = (df.isnull().sum(axis=0) / len(df)).sort_values(ascending=False).index
    null_data_test = pd.concat([
        df.isnull().sum(axis=0),
        (df.isnull().sum(axis=0) / len(df)).sort_values(ascending=False),
        df.loc[:, df.columns.isin(list(null_test))].dtypes], axis=1)
    null_data_test = null_data_test.rename(columns={0: '# null',
                                                    1: '% null',
                                                    2: 'type'}).sort_values(ascending=False, by='% null')
    null_data_test = null_data_test[null_data_test["# null"] != 0]

    return null_data_test


def types(df):
    return pd.DataFrame(df.dtypes, columns=['Type'])


def forecasting_autoarima(y_train, y_test, s):
    fh = np.arange(len(y_test)) + 1
    forecaster = AutoARIMA(sp=s)
    forecaster.fit(y_train)
    y_pred = forecaster.predict(fh)
    plot_series(y_train, y_test, y_pred, labels=["y_train", "y_test", "y_pred"])
    st.pyplot()


def main():
    st.sidebar.title("What to do")
    activities = ["Exploratory Data Analysis", "Plotting and Visualization", "Building Model", "About"]
    choice = st.sidebar.selectbox("Select Activity", activities)
    # Add a slider to the sidebar:
    st.sidebar.markdown("# Lang")
    x = st.sidebar.slider(
        'Select a lang for ACF and PACF analysis',
        50, 60
    )
    # Add a slider to the sidebar:
    st.sidebar.markdown("# Seasonal")
    s = st.sidebar.slider(
        'Select a seasonal parameter from previous ACF and PACF analysis',
        24, 48
    )
    # cloud logo
    #st.sidebar.title("Built on:")
    #st.sidebar.image("src/ibmcloud_logo.png", width=200)
    # Upload file
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None and choice == "Exploratory Data Analysis":
        data = pd.read_csv(uploaded_file)
        st.subheader(choice)
        # Show dataset
        if st.checkbox("Show Dataset"):
            rows = st.number_input("Number of rows", 5, len(data))
            st.dataframe(data.head(rows))
        # Show columns
        if st.checkbox("Columns"):
            st.write(data.columns)
        # Data types
        if st.checkbox("Column types"):
            st.write(types(data))
        # Show Shape
        if st.checkbox("Shape of Dataset"):
            data_dim = st.radio("Show by", ("Rows", "Columns", "Shape"))
            if data_dim == "Columns":
                st.text("Number of Columns: ")
                st.write(data.shape[1])
            elif data_dim == "Rows":
                st.text("Number of Rows: ")
                st.write(data.shape[0])
            else:
                st.write(data.shape)
        # Check null values in dataset
        if st.checkbox("Check null values"):
            nvalues = null_values(data)
            st.write(nvalues)
        # Show Data summary
        if st.checkbox("Show Data Summary"):
            st.text("Datatypes Summary")
            st.write(data.describe())
        # Plot time series, ACF and PACF
        if st.checkbox("Select column as time series"):
            columns = data.columns.tolist()
            selected = st.multiselect("Choose", columns)
            series = data[selected]
            if st.button('Plot Time Series, ACF and PACF'):
                tsplot(series, lags=x)
                st.pyplot()

    elif uploaded_file is not None and choice == "Plotting and Visualization":
        st.subheader(choice)
        data = pd.read_csv(uploaded_file)
        df = data.copy()
        all_columns = df.columns.tolist()
        type_of_plot = st.selectbox("Select Type of Plot",
                                    ["area", "line", "scatter", "pie", "bar", "correlation", "distribution"])

        if type_of_plot == "line":
            select_columns_to_plot = st.multiselect("Select columns to plot", all_columns)
            cust_data = df[select_columns_to_plot]
            st.line_chart(cust_data)

        elif type_of_plot == "area":
            select_columns_to_plot = st.multiselect("Select columns to plot", all_columns)
            cust_data = df[select_columns_to_plot]
            st.area_chart(cust_data)

        elif type_of_plot == "bar":
            select_columns_to_plot = st.multiselect("Select columns to plot", all_columns)
            cust_data = df[select_columns_to_plot]
            st.bar_chart(cust_data)

        elif type_of_plot == "pie":
            select_columns_to_plot = st.selectbox("Select a column", all_columns)
            st.write(df[select_columns_to_plot].value_counts().plot.pie())
            st.pyplot()

        elif type_of_plot == "correlation":
            st.write(sns.heatmap(df.corr(), annot=True, linewidths=.5, annot_kws={"size": 7}))
            st.pyplot()

        elif type_of_plot == "scatter":
            st.write("Scatter Plot")
            scatter_x = st.selectbox("Select a column for X Axis", all_columns)
            scatter_y = st.selectbox("Select a column for Y Axis", all_columns)
            st.write(sns.scatterplot(x=scatter_x, y=scatter_y, data=df))
            st.pyplot()

        elif type_of_plot == "distribution":
            select_columns_to_plot = st.multiselect("Select columns to plot", all_columns)
            st.write(sns.distplot(df[select_columns_to_plot]))
            st.pyplot()

    elif uploaded_file is not None and choice == "Building Model":
        st.subheader(choice)
        data = pd.read_csv(uploaded_file)
        df = data.copy()
        st.write("Select the columns to use for training")
        columns = df.columns.tolist()
        selected_column = st.multiselect("Select Columns", columns)
        new_df = df[selected_column]
        st.write(new_df)

        if st.checkbox("Train/Test Split"):
            y_train, y_test = temporal_train_test_split(new_df.T.iloc[0])
            st.text("Train Shape")
            st.write(y_train.shape)
            st.text("Test Shape")
            st.write(y_test.shape)
            plot_series(y_train, y_test, labels=["y_train", "y_test"])
            st.pyplot()

        if st.button("Training a Model"):
            model_selection = st.selectbox("Model to train", ["AutoArima", "LSTM", "MLP", "RNN"])
            if model_selection == "AutoArima":
                y_train, y_test = temporal_train_test_split(new_df.T.iloc[0])
                forecasting_autoarima(y_train, y_test, s)

    elif choice == "About":
        st.title("About")
        st.write("The app developed by Alexander Robles.")
        st.write("Stack: Python, Streamlit, Docker, Kubernetes")


if __name__ == "__main__":
    main()