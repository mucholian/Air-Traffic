library(Matrix)
library(coefplot)
library(glmnet)
attach(all_data)
library(useful)
library(readr)
library(readxl)
library(ggplot2)
library(dplyr)
library(lubridate)
library(openxlsx)
library(ggthemes)
library(magrittr)
library(rio)
library(chron)
library(tidyverse)
library(lazyeval)
library(purrr)
library(shiny)
# library(glue)
library(zoo)
library(plyr)
library(jsonlite)
library(httr)
library(curl)
library(rvest)
#library(ggmap)
#library(RColorBrewer)
library(leaflet)
#library(splashr)
#library(PythonInR)
library(docker)
library(devtools)
library(RCurl)
#library(magick)
library(XML)
library(rJava)
library(EIAdata)
library(data.table)
library(coefplot)
# library(Rblpapi)
#library(smooth)
#library(Mcomp)
library(EIAdata)
library(data.table)
#library(stringr)
#library(xlsx)

# all_data <- read.csv('C:/Users/Moses/Python/everything_4.xlsx')

all_data <- read_xlsx('C:/Users/Moses/Python/everything_6.xlsx',sheet='sheet')
all_data <- all_data[-c(1)]
colnames(all_data)


valueFormula <- LA_NY_2 ~ P5_MILES + P1_MILES + CH_P1_MILES + CH_P1_MILES + LA_NY_3 + P1_ST + P5_ST + P5_PR + P1_PR + P1_IMP + P5_IMP + P5_ST_DR + US_ST_DR + P1_ST_DR + CH_US_DEM + US_EXP + HO_1_3 + HO_2_3 + HO_1_2 + 
    CH_P1_PR + CH_P5_PR + CL_2_3 + CL_1_3 + CL_1_2 + NY_J_1_2 + NY_J_1_3 - 1

# CL_M2_M3 + CL_M1_M3 + CL_M1_M2 have to tripple check expiry

value_1 = glm(valueFormula, data=all_data)

coefplot(value_1, sort='magnitude')

manX_Train <- build.x(valueFormula, data=all_data,contrasts=FALSE, sparse=TRUE)
manY_Train <- build.y(valueFormula, data=all_data)

value2 <- glmnet(x=manX_Train, y=manY_Train,family='gaussian')

plot(value2, xvar='lambda')
coefpath(value2)
plot(value2)

animation::cv.ani(k=5)

value3 <- cv.glmnet(x=manX_Train, y=manY_Train,
                    family='gaussian',
                    nfolds=5)
plot(value3)
coefpath(value3)

coefplot(value3, sort='magnitude', lambda='lambda.min')
coefplot(value3, sort='magnitude', lambda='lambda.min',plot=FALSE)

coefplot(value3, sort='magnitude', lambda=0.01)
coefplot(value3, sort='magnitude', lambda=3)


value4 <- cv.glmnet(x=manX_Train, y=manY_Train,
                    family='gaussian',
                    nfolds=5, alpha=0)
coefpath(value4)
coefplot(value4, sort='magnitude', lambda='lambda.min')
coefplot(value4, sort='magnitude', lambda='lambda.min')
