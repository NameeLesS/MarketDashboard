window.startTour = function() {
    if (!window.driver || !window.driver.js || !window.driver.js.driver) {
        console.error("driver.js library is not loaded.");
        return;
    }

    const driverObj = window.driver.js.driver({
        showProgress: true,
        steps: [
            {
                popover: {
                    title: 'Game Market Analyzer',
                    description: 'Game Market Analyzer is a tool that lets you analyze the game market and gain the crucial insights that will help you create better games and make informed business decisions in the future.'
                }
            },
            {
                element: '#sidebar-tabs',
                popover: {
                    title: 'Navigation',
                    description: 'The Game Market Analyzer is divided into three sections, Overview, Explore and Insight. Each section serves a different purpose.'
                }
            },
            {
                element: '#sidebar-overview-tab',
                popover: {
                    title: 'Overview',
                    description: 'Open the overview section.'
                }
            },
            {
                popover: {
                    title: 'Overview Details',
                    description: 'Overview section gives you the high level view of the market. It shows you the general information about the market like size, trends, seasonality information etc.'
                }
            },
            {
                element: '#overview-genre-dropdown',
                popover: {
                    title: 'Genre Filter',
                    description: 'Here you can filter the information by the genre. This influences all the elements on this page.'
                }
            },
            {
                element: '#overview-period-buttons',
                popover: {
                    title: 'Time Period',
                    description: 'Here by clicking on the appropriate button you can select the period by which we should aggregate the data.'
                }
            },
            {
                element: '#overview-range-buttons',
                popover: {
                    title: 'Data Range',
                    description: 'Here you can limit the range of the data that will be displayed on the charts below. It shows the data.'
                }
            },
            {
                element: '#overview-pie-year-dropdown',
                popover: {
                    title: 'Year Selection',
                    description: 'This dropdown lets you select the year for which you would like to check the game characteristics.'
                }
            },
            {
                element: '#sidebar-explore-tab',
                popover: {
                    title: 'Switch to Explore',
                    description: 'Now lets switch to the explore section.',
                    onNextClick: () => {
                        const tab = document.getElementById('sidebar-explore-tab');
                        if (tab) { tab.click(); }
                        setTimeout(() => {
                            driverObj.moveNext();
                        }, 500);
                    }
                }
            },
            {
                popover: {
                    title: 'Explore Section',
                    description: 'Explore section lets you explore the data. It was designed to let you explore the similarities and characteristics of the segment of the market that is in your interest.'
                }
            },
            {
                element: '#explore-filters-panel',
                popover: {
                    title: 'Filters',
                    description: 'Here you can filter the data by specifyifing the exact characteristics of the data.'
                }
            },
            {
                element: '#explore-peak-ccu-histogram',
                popover: {
                    title: 'Histogram Selection',
                    description: 'You can also select the games within certain range of top activity in this histogram.'
                }
            },
            {
                element: '#explore-table-tour-target',
                popover: {
                    title: 'Data Table',
                    description: 'The filtered data appears here. You can adjust the granularity of the information about the games, by selecting the attributes that are in your interest.'
                }
            },
            {
                element: '#explore-table-tour-target',
                popover: {
                    title: 'Highlighting',
                    description: 'By clicking on a specific instance, this instance will be highlighted on the other plots in this section.'
                }
            },
            {
                element: '#explore-scatter-plot',
                popover: {
                    title: 'Similar Products',
                    description: 'This plot lets you analyze the similar products, define the distance between these products.'
                }
            },
            {
                element: '#explore-distance-buttons',
                popover: {
                    title: 'Distance Metric',
                    description: 'You can select the distance by which measured the similarity between products.'
                }
            },
            {
                element: '#explore-scatter-color-by',
                popover: {
                    title: 'Color Attribute',
                    description: 'And also you can select the attribute by which the data should be colored.'
                }
            },
            {
                element: '#explore-sentiment-graphs',
                popover: {
                    title: 'Sentiment Influence',
                    description: 'These plots let you analyze the influence of the sentiment on the game success.'
                }
            },
            {
                element: '#sidebar-insights-tab',
                popover: {
                    title: 'Switch to Insights',
                    description: 'Now lets switch to the insights section.',
                    onNextClick: () => {
                        const tab = document.getElementById('sidebar-insights-tab');
                        if (tab) { tab.click(); }
                        setTimeout(() => {
                            driverObj.moveNext();
                        }, 500);
                    }
                }
            },
            {
                popover: {
                    title: 'Insights Section',
                    description: 'Insights section was designed to let you derive the useful information that will help you make the informed business decisions. It lets you analyze what is worth to invest for and how the final product should look like if we want to maximize the revenue.'
                }
            },
            {
                element: '#insights-global-genre-dropdown',
                popover: {
                    title: 'Genre Focus',
                    description: 'Here again you can select the genre that you are interested in.'
                }
            },
            {
                element: '#insights-treemap-graph',
                popover: {
                    title: 'Income Potential',
                    description: 'This graph lets you analyze what type of games have the potential to maximize your income.'
                }
            },
            {
                element: '#insights-radar-subplots-graph',
                popover: {
                    title: 'Benchmarking',
                    description: 'Here you can analyze how the Genre leaders differ from the average game of category.'
                }
            },
            {
                element: '#insights-income-violin-graph',
                popover: {
                    title: 'Pricing Strategy',
                    description: 'This graph lets you decide on the price of your game.'
                }
            }
        ]
    });
    driverObj.drive();
};
