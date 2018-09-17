
# coding: utf-8

# # Infrastructure Triggers

# ### Berths

# In[3]:


def berth_trigger():
    
    allowable_berth_occupancy = 0.40

    for i in range(1,1+len(berths)):
        berths[0].occupancy_calc(i)
        if berths[0].occupancy < allowable_berth_occupancy:
            return i 

