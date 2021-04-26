# Alex DeLuca
# Some quick EDA

library(tidyverse)


fires <- read_csv('data/fires_cleaned/final_fires_cleaned.csv')


top_fires <- fires %>%
  select(year = FIRE_YEAR, fsize = FIRE_SIZE, fid = OBJECTID) %>%
  group_by(year) %>%
  mutate(total_area =  sum(fsize),
         pct_area = fsize/total_area,
         year_fires = n()) %>%
  arrange(year, desc(pct_area)) %>%
  mutate(cum_pct = cumsum(pct_area)) %>%
  filter(cum_pct < .90) %>%
  summarise(f90 = n(),
            n_fires = year_fires[1],
            total_burn = total_area[1])



top_fires %>%
  ggplot(aes(x = year, y = f90/n_fires))  +
  ylim(0, NA) +
  geom_line() +
  geom_point()

top_fires %>%
  ggplot(aes(x = year, y = total_burn))  +
  ylim(0, NA) +
  geom_line() +
  geom_point()


cor(top_fires$f90/top_fires$n_fires, top_fires$total_burn )

