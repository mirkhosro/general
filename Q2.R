library('plyr')
library('stringr')
options(digits=10)

base.folder = '~/Data/DI_challenge/'
setwd(base.folder)

rt <- read.csv('realtime.csv', stringsAsFactors=FALSE)
rt$timestamp <- strptime(rt$timestamp, "%Y-%m-%d %H:%M:%S")
rt$timestamp <- as.POSIXct(rt$timestamp)  # convert to POSICct so we can store in DF
rt$vehicle_id <- as.factor(rt$vehicle_id)
rt$dist_along_route <- as.numeric(rt$dist_along_route)

# PART 1: What is the median number of trips made by a single vehicle?
# Find unique pairs of trips and vehicles
trips.n.vehicles <- unique(rt[c('trip_id', 'vehicle_id')])
# Form the number of trips for each vehicle
vehicles <- ddply(trips.n.vehicles, "vehicle_id", summarize, trip.count=length(trip_id))
# Result
median(vehicles$trip.count)

# PART 2: What was the highest total number of trips made by a 
# Manhattan bus route (for our purposes all routes starting with "M")?
# I detected the Manhattan bus route name patterns by looking at the values
# starting with M in routes.txt file's route_id column
pattern <- "M[1-9]\\d*A?\\+?"
# Actual routes seen on that date
route_id <- str_extract(rt$trip_id, pattern)
# Add a column for the extracted route_id's to rt
rt <- cbind(rt, route_id)
# Keep data only for Manhattan routes
manhattan <- subset(rt, !is.na(rt$route_id))
# Find unique Manhattan trips and their respective route id's
manhattan.trips <- unique(manhattan[c('trip_id', 'route_id')])
# Form the counts by route_id
manhattan.counts <- ddply(manhattan.trips, .(route_id), summarize, trip.count=length(trip_id))
# Result = 600
max(manhattan.counts$trip.count)  

# PART 3: What is the second-highest average speed - in Miles Per Hour - across all bus routes in Manhattan?
dist.n.time <- function(x) {
  # this function estimates the distance traveled and time taken in a given trip 
  # distance is taken as the difference between the largest and smallest distance
  # traveled and the largest and smallest time along the route.
  # it is not accurate because it cannot take into account the distance and time
  # of the first stop. also it assumes monotone increasing time and distances which
  # may not hold for all trips
  dist <- x$dist_along_route
  trip.dist <- max(dist, na.rm=TRUE) - min(x$dist_along_route, na.rm=TRUE)
  trip.time <- max(x$timestamp) - min(x$timestamp)
  units(trip.time) <- 'secs'
  data.frame(trip.dist, trip.time)
}

METERS_PER_MILE = 1609.34
# compute distance traveled and time elasped for each trip
by.trip <- ddply(manhattan, .(route_id, vehicle_id, trip_id), dist.n.time)
# aggregate at route level and calculate the average speed
by.route <- ddply(by.trip, .(route_id), summarize, route.dist=sum(trip.dist), route.time=sum(trip.time))
units(by.route$route.time) <- 'hours'
by.route$avg.speed <- by.route$route.dist / as.double(by.route$route.time) / METERS_PER_MILE
# Result = 6.253972
by.route$avg.speed[order(by.route$avg, decreasing=TRUE)][2]

#by.vehicle <- ddply(by.trip, .(route_id, vehicle_id), summarize, veh.dist=sum(trip.dist), veh.time=sum(trip.time))
#units(by.vehicle$veh.time) <- 'hours'
#by.vehicle$avg.speed <- by.vehicle$veh.dist / as.double(by.vehicle$veh.time) / METERS_PER_MILE
#by.route2 <- ddply(by.vehicle, .(route_id), summarize, avg.speed=mean(avg.speed))

# PART 4: Compute the variance of all reported headways across all stations
# (excluding the initial station, where buses often idle) on the M116's S/W 
# direction. Give your answer in minutes^2.
m116 <- subset(manhattan, route_id == 'M116')
b <- subset(m116, vehicle_id == 6670)
