
# coding: utf-8

# In[2]:


import matplotlib.pyplot as plt


# In[ ]:


def plot_trend(maize, soybean, wheat, width, height):
    fig  = plt.figure(figsize=(width, height))
    grid = plt.GridSpec(1, 1, wspace=0.4, hspace=0.5)
    fig1 = fig.add_subplot(grid[0, 0])

    fig1.plot(maize.years, maize.demand    , label='Maize demand')
    fig1.plot(soybean.years, soybean.demand, label='Soybean demand')
    fig1.plot(wheat.years, wheat.demand    , label='Wheat demand')
    fig1.set_title ('Commodity demand')
    fig1.set_xlabel('Year')
    fig1.set_ylabel('Demand [t/y]')
    fig1.legend()

    return fig1

