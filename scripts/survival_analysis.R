# Loading the necessary libraries, adding dplyr for relational data merging
library(DBI)
library(RPostgres)
library(survival)
library(survminer)
library(dotenv)
library(dplyr)

# Loading the hidden credentials from our root .env file
load_dot_env(file = ".env")

# Connecting to the PostgreSQL database safely
print("Establishing connection to the coastal_catch database...")
con <- dbConnect(
  RPostgres::Postgres(),
  dbname = Sys.getenv("DB_NAME"),
  host = Sys.getenv("DB_HOST"),
  port = Sys.getenv("DB_PORT", unset = "5432"),
  user = Sys.getenv("DB_USER"),
  password = Sys.getenv("DB_PASSWORD")
)

# Fetching the catch logs and the environmental conditions into R DataFrames
print("Retrieving catch logs and environmental data...")
catch_data <- dbGetQuery(con, "SELECT * FROM catch_logs")
env_data <- dbGetQuery(con, "SELECT * FROM environmental_conditions")

# Disconnecting from the database safely 
dbDisconnect(con)

# Performing a rolling join to attach the most recent weather reading to each fishing trip
print("Merging covariates into the analytical dataset...")
analytical_dataset <- catch_data %>%
  left_join(env_data, join_by(closest(start_time >= reading_time)))

# Displaying the merged dataset to verify the join was successful
print("Viewing the final analytical dataset:")
head(analytical_dataset)

# Creating the core survival object
surv_object <- Surv(time = analytical_dataset$time_to_bite_minutes, event = analytical_dataset$event_occurred)

# Fitting the Cox Proportional Hazards Model using temperature and pressure as covariates
print("Fitting the Cox Proportional Hazards Model...")
cox_model <- coxph(surv_object ~ water_temperature_f + barometric_pressure_mb, data = analytical_dataset)

# Printing the statistical summary of the hazard ratios
summary(cox_model)