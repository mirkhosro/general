library('plyr')
library('ggplot2')

base.folder = '~/Data/DI_challenge/'
setwd(base.folder)

bbc <- read.csv('bbcnews.csv')
bbc <- subset(bbc, type %in% c('video', 'photo', 'link'))
bbc$type <- factor(bbc$type)

get.hour <- function(t, interval=6, offset=0) {
  tod <- strptime(t, '%H:%M:%S', 'GMT')
  hr <- tod$hour
  hr <- as.integer(((hr-offset) %% 24) / interval) * interval + offset
  str_c(str_pad(hr, 2, pad="0"), "-", str_pad((hr+interval) %% 24, 2, pad="0"))
}

bbc$hour <- as.factor(get.hour(bbc$time, 3))
# remove potential outliers
bbc <- subset(bbc, likes_count < 50000)

## effect of message length
#bbc.links <- subset(bbc, type=='link')
plot1 <- qplot(x=message_length, y=likes_count, data=bbc, color=type, xlab="message length",
         ylab="number of likes", main="Likes by message length")
plot1 <- plot1 + theme(text=element_text(size=20))
print(plot1)

l1 <- lm(likes_count~message_length, data=bbc,subset=(type=='video'))
summary(l1)
l2 <- lm(likes_count~message_length, data=bbc,subset=(type=='photo'))
summary(l2)
l3 <- lm(likes_count~message_length, data=bbc,subset=(type=='link'))
summary(l3)

## effect of post type
m1 <- lm(likes_count ~ type, data=bbc)
summary(m1)
m2 <- lm(shares_count ~ type, data=bbc)
summary(m2)
m3 <- lm(comments_count ~ type, data=bbc)
summary(m3)

get_summary <- function(data, varname, byvars, metric) {
  summary_f <- function(x, col) {
    c(mean=mean(x[[col]]))
  }
  data_sum <- ddply(data, byvars, summary_f, varname)
  data_sum$mean <- data_sum$mean / mean(data_sum$mean)
  data_sum$Metric <- metric
  data_sum
}
likes <- get_summary(bbc, 'likes_count', 'type', 'Likes')
shares <- get_summary(bbc, 'shares_count', 'type', 'Shares')
comments <- get_summary(bbc, 'comments_count', 'type', 'Comments')
all <- rbind(likes, comments, shares)
plot2 <- ggplot(all, aes(x=type, y=mean, fill=Metric)) +
  geom_bar(stat="identity", color="black", width=0.5, position=position_dodge()) +
  labs(title="Average likes, shares & comments by post type", x="Type", y="Average (normalized)") +
  theme(text=element_text(size=20))
print(plot2)

## effect of posting time
levels(bbc$hour)
bbc$hour <- relevel(bbc$hour, "06-09")
n1 <- lm(likes_count ~ hour, data=bbc)
summary(n1)
n2 <- lm(shares_count ~ hour, data=bbc)
summary(n2)
n3 <- lm(comments_count ~ hour, data=bbc)
summary(n3)

## everything together
b1 <- lm(likes_count ~ type + hour + message_length, data=bbc)
summary(b1)
b2 <- lm(shares_count ~ type + hour + message_length, data=bbc)
summary(b2)
b3 <- lm(comments_count ~ type + hour + message_length, data=bbc)
summary(b3)



