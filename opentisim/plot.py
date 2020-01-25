# package(s) for data handling
import matplotlib.pyplot as plt

# *** General functions
def cashflow_plot(Terminal, cash_flows, title='Cash flow plot', width=0.2, alpha=0.6, fontsize=20):
    """Gather data from Terminal elements and combine into a cash flow plot"""

    # prepare years, revenue, capex and opex for plotting
    years = cash_flows['year'].values
    revenues = cash_flows['revenues'].values
    capex = cash_flows['capex'].values
    opex = cash_flows['insurance'].values + cash_flows['maintenance'].values + cash_flows['energy'].values + \
           cash_flows['labour'].values + cash_flows['demurrage'].values

    # sum cash flows to get profits as a function of year
    profits = []
    for year in years:
        profits.append(-cash_flows.loc[cash_flows['year'] == year]['capex'].item() -
                       cash_flows.loc[cash_flows['year'] == year]['insurance'].item() -
                       cash_flows.loc[cash_flows['year'] == year]['maintenance'].item() -
                       cash_flows.loc[cash_flows['year'] == year]['energy'].item() -
                       cash_flows.loc[cash_flows['year'] == year]['labour'].item() -
                       cash_flows.loc[cash_flows['year'] == year]['demurrage'].item() +
                       cash_flows.loc[cash_flows['year'] == year]['revenues'].item())

    # cumulatively sum profits to get profits_cum
    profits_cum = [None] * len(profits)
    for index, value in enumerate(profits):
        if index == 0:
            profits_cum[index] = profits[index]
        else:
            profits_cum[index] = profits_cum[index - 1] + profits[index]

    # generate plot canvas
    fig, ax1 = plt.subplots(figsize=(20, 12))

    colors = ['mediumseagreen', 'firebrick', 'steelblue']

    # print capex, opex and revenue
    ax1.bar([x for x in years], -capex, zorder=1, width=width, alpha=alpha, label="capex", color=colors[1],
            edgecolor='darkgrey')
    ax1.bar([x - width for x in years], -opex, zorder=1, width=width, alpha=alpha, label="opex", color=colors[0],
            edgecolor='darkgrey')
    ax1.bar([x + width for x in years], revenues, zorder=1, width=width, alpha=alpha, label="revenue", color=colors[2],
            edgecolor='darkgrey')

    # print profits (annual and cumulative)
    ax1.step(years, profits, zorder=2, label='profits', where='mid')
    ax1.step(years, profits_cum, zorder=2, label='profits_cum', where='mid')

    # title and labels
    ax1.set_title(title, fontsize=fontsize)
    ax1.set_xlabel('Years', fontsize=fontsize)
    ax1.set_ylabel('Cashflow [M $]', fontsize=fontsize)
    # todo: check the units

    # ticks and tick labels
    ax1.set_xticks([x for x in years])
    ax1.set_xticklabels([int(x) for x in years], rotation='vertical', fontsize=fontsize)
    ax1.yaxis.set_tick_params(labelsize=fontsize)

    # add grid
    ax1.grid(zorder=0, which='major', axis='both')

    # print legend
    fig.legend(loc='lower center', bbox_to_anchor=(0, -.01, .9, 0.7),
               fancybox=True, shadow=True, ncol=5, fontsize=fontsize)
    fig.subplots_adjust(bottom=0.15)

