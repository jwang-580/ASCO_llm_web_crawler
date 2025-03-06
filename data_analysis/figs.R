library(ggplot2)
library(dplyr)
library(tidyr)
library(scales)
library(ggsci)


####### Figure 2A, COIs and specific COI change over time #######
# Create data frame from the provided information
periods <- c("2010-2015", "2015-2020", "2020-2025")

# Create data frame with percentages
coi_data <- data.frame(
  Period = periods,
  Any_COI = c(70.0, 77.0, 72.0),
  Employment = c(31.3, 38.3, 36.2),
  Advisory = c(52.5, 61.5, 59.1),
  Honoraria = c(43.8, 49.4, 48.8),
  `Speakers Bureau` = c(NA, 26.0, 30.9)
)

# Convert to long format for ggplot
coi_long <- coi_data %>%
  pivot_longer(cols = -Period, 
               names_to = "COI_Type", 
               values_to = "Percentage") %>%
  # Filter out the types we don't want to show in the line graph
  filter(COI_Type %in% c("Any_COI", "Employment", "Advisory", "Honoraria"))

# Set the order of COI types for the legend
coi_long$COI_Type <- factor(coi_long$COI_Type, 
                            levels = c("Any_COI", "Employment", "Advisory", "Honoraria"))

# Create the plot using JCO color palette
p2_a <- ggplot(coi_long, aes(x = Period, y = Percentage, group = COI_Type, color = COI_Type)) +
  geom_line(size = 1.2) +
  geom_point(size = 3) +
  scale_y_continuous(limits = c(0, 100), 
                     breaks = seq(0, 100, by = 20),
                     labels = function(x) paste0(x, "%")) +
  scale_color_jco() +  # Use JCO color palette from ggsci
  labs(title = "COIs in Oncology Trials Over Time",
       x = "",
       y = "Percentage of Studies (%)",
       color = NULL) +
  theme_minimal() +
  theme(
    text = element_text(family = "Arial", size = 12),
    plot.title = element_text(size = 12, face = "bold", hjust = 0.5),
    axis.title = element_text(size = 12, face = "bold"),
    axis.text = element_text(size = 12),
    legend.title = element_text(size = 10, face = "bold"),
    legend.text = element_text(size = 10),
    legend.position = "bottom",
    panel.grid.major.y = element_line(color = "gray90", linetype = "dashed"),
    panel.grid.major.x = element_blank(),
    panel.grid.minor = element_blank(),
    panel.background = element_rect(fill = "white", color = NA),
    plot.background = element_rect(fill = "white", color = NA)
  )

# Add data labels
p2_a <- p2_a + geom_text(aes(label = paste0(Percentage)), 
                   vjust = -0.8, color = "black", size = 3)

print (p2_a)


##### Figure 2B, percentage of authors with COIs ######

# Create data frame for the proportion of authors with COIs
# Format: Each row represents a COI type, with columns for the three time periods
# For each period, we have median, Q1, and Q3 values

# Create the data frame
coi_proportion <- data.frame(
  COI_Type = c("Any COI", "Employment", "Advisory", "Honoraria"),
  
  # Period 1 (2010-2015)
  Period1_Median = c(31.2, 20.0, 16.7, 13.3),
  Period1_Q1 = c(12.5, 13.3, 9.09, 7.85), 
  Period1_Q3 = c(56.2, 30.6, 28.6, 25.0),
  
  # Period 2 (2015-2020)
  Period2_Median = c(36.4, 18.8, 17.6, 13.0),
  Period2_Q1 = c(15.8, 11.7, 9.3, 7.14),
  Period2_Q3 = c(62.3, 27.9, 33.3, 21.1),
  
  # Period 3 (2020-2025)
  Period3_Median = c(37.5, 16.7, 21.4, 13.0),
  Period3_Q1 = c(15.1, 9.5, 11.3, 6.25),
  Period3_Q3 = c(66.7, 26.6, 35.7, 23.5)
)

# Reshape data to long format for ggplot
coi_long <- coi_proportion %>%
  pivot_longer(
    cols = -COI_Type,
    names_to = c("Period", ".value"),
    names_pattern = "Period(.*)_(.*)"
  ) %>%
  mutate(Period = case_when(
    Period == "1" ~ "2010-2015",
    Period == "2" ~ "2015-2020",
    Period == "3" ~ "2020-2025"
  ))

# Set the order of COI types for the legend
coi_long$COI_Type <- factor(coi_long$COI_Type, 
                            levels = c("Any COI", "Employment", "Advisory","Honoraria"))

# Create the boxplot with time on x-axis
p2_b <- ggplot(coi_long, aes(x = Period, y = Median, fill = COI_Type)) +
  geom_boxplot(
    aes(ymin = Q1, lower = Q1, middle = Median, upper = Q3, ymax = Q3),
    stat = "identity",
    position = position_dodge(width = 0.8),
    width = 0.7
  ) +
  scale_fill_jco() +
  labs(
    title = "Proportion of Authors with COIs",
    x = "",
    y = "Percentage of Authors (%)",
    fill = NULL  # Remove legend title
  ) +
  scale_y_continuous(
    limits = c(0, 100),
    breaks = seq(0, 100, by = 20),
    labels = function(x) paste0(x, "%")
  ) +
  theme_minimal() +
  theme(
    text = element_text(family = "Arial", size = 12),
    plot.title = element_text(size = 12, face = "bold", hjust = 0.5),
    axis.title = element_text(size = 12, face = "bold"),
    axis.text = element_text(size = 10),
    legend.text = element_text(size = 10),
    legend.position = "bottom",
    panel.grid.major.y = element_line(color = "gray90", linetype = "dashed"),
    panel.grid.major.x = element_blank(),
    panel.grid.minor = element_blank(),
    panel.background = element_rect(fill = "white", color = NA),
    plot.background = element_rect(fill = "white", color = NA)
  )

# Add data labels for median values
p2_b <- p2_b + geom_text(
  aes(label = paste0(Median), group = COI_Type),
  position = position_dodge(width = 0.8),
  vjust = -0.5,
  size = 3
)

print(p2_b)


####### Figure 3A, US-specific COIs and specific COI change over time #######
# Create data frame from the provided information
periods <- c("2010-2015", "2015-2020", "2020-2025")

# Create data frame with percentages
coi_data <- data.frame(
  Period = periods,
  Any_COI = c(75.2, 82.8, 76.0),
  Employment = c(32.8, 44.6, 41.2),
  Advisory = c(54.0, 65.8, 65.8),
  Honoraria = c(39.0, 44.9, 46.3)
)

# Convert to long format for ggplot
coi_long <- coi_data %>%
  pivot_longer(cols = -Period, 
               names_to = "COI_Type", 
               values_to = "Percentage") %>%
  # Filter out the types we don't want to show in the line graph
  filter(COI_Type %in% c("Any_COI", "Employment", "Advisory", "Honoraria"))

# Set the order of COI types for the legend
coi_long$COI_Type <- factor(coi_long$COI_Type, 
                            levels = c("Any_COI", "Employment", "Advisory", "Honoraria"))

# Create the plot using JCO color palette
p3_a <- ggplot(coi_long, aes(x = Period, y = Percentage, group = COI_Type, color = COI_Type)) +
  geom_line(size = 1.2) +
  geom_point(size = 3) +
  scale_y_continuous(limits = c(0, 100), 
                     breaks = seq(0, 100, by = 20),
                     labels = function(x) paste0(x, "%")) +
  scale_color_jco() +  # Use JCO color palette from ggsci
  labs(title = "COIs in US-Led Oncology Trials Over Time",
       x = "",
       y = "Percentage of Studies (%)",
       color = NULL) +
  theme_minimal() +
  theme(
    text = element_text(family = "Arial", size = 12),
    plot.title = element_text(size = 12, face = "bold", hjust = 0.5),
    axis.title = element_text(size = 12, face = "bold"),
    axis.text = element_text(size = 12),
    legend.title = element_text(size = 10, face = "bold"),
    legend.text = element_text(size = 10),
    legend.position = "bottom",
    panel.grid.major.y = element_line(color = "gray90", linetype = "dashed"),
    panel.grid.major.x = element_blank(),
    panel.grid.minor = element_blank(),
    panel.background = element_rect(fill = "white", color = NA),
    plot.background = element_rect(fill = "white", color = NA)
  )

# Add data labels
p3_a <- p3_a + geom_text(aes(label = paste0(Percentage)), 
                         vjust = -0.8, color = "black", size = 3)

print (p3_a)


##### Figure 3b, US vs non-US based on COI types #####
# Define the data
US <- c(868, 435, 684, 481)
non_US <- c(730, 336, 573, 552)

total_US <- 1118
total_non_US <- 1085

# Calculate percentages
US_percentages <- (US / total_US) * 100
non_US_percentages <- (non_US / total_non_US) * 100

# Create a data frame for plotting
coi_data <- data.frame(
  Category = rep(c("Any", "Employment", "Advisory", "Honoraria"), 2),
  Region = c(rep("US", 4), rep("Non-US", 4)),
  Percentage = c(US_percentages, non_US_percentages)
)

# Set the order of categories and regions
coi_data$Category <- factor(coi_data$Category, levels = c("Any", "Employment", "Advisory", "Honoraria"))
coi_data$Region <- factor(coi_data$Region, levels = c("US", "Non-US"))

# Create the plot
p3_b <- ggplot(coi_data, aes(x = Category, y = Percentage, fill = Region)) +
  geom_bar(stat = "identity", position = position_dodge(width = 0.9), width = 0.7) +
  scale_y_continuous(limits = c(0, 100), 
                     breaks = seq(0, 100, by = 20),
                     labels = function(x) paste0(x, "%")) +
  scale_fill_jco() +  # Use JCO color palette from ggsci
  labs(title = "COIs in US vs Non-US Studies",
       x = "",
       y = "Percentage of Studies (%)",
       fill = NULL) +
  theme_minimal() +
  theme(
    text = element_text(family = "Arial", size = 12),
    plot.title = element_text(size = 12, face = "bold", hjust = 0.5),
    axis.title = element_text(size = 12, face = "bold"),
    axis.text = element_text(size = 12),
    legend.title = element_text(size = 10, face = "bold"),
    legend.text = element_text(size = 10),
    legend.position = "bottom",
    panel.grid.major.y = element_line(color = "gray90", linetype = "dashed"),
    panel.grid.major.x = element_blank(),
    panel.grid.minor = element_blank(),
    panel.background = element_rect(fill = "white", color = NA),
    plot.background = element_rect(fill = "white", color = NA)
  )

# Add data labels
p3_b <- p3_b + geom_text(aes(label = sprintf("%.1f%%", Percentage), 
                             y = Percentage + 3,
                             group = Region),
                         position = position_dodge(width = 0.9),
                         color = "black", size = 3)

# Calculate p-values for annotation
COI_all <- matrix(c(US[1], total_US - US[1], non_US[1], total_non_US - non_US[1]), nrow=2, byrow=TRUE)
COI_employment <- matrix(c(US[2], total_US - US[2], non_US[2], total_non_US - non_US[2]), nrow=2, byrow=TRUE)
COI_advisory <- matrix(c(US[3], total_US - US[3], non_US[3], total_non_US - non_US[3]), nrow=2, byrow=TRUE)
COI_honoraria <- matrix(c(US[4], total_US - US[4], non_US[4], total_non_US - non_US[4]), nrow=2, byrow=TRUE)

p_values <- c(
  chisq.test(COI_all)$p.value,
  chisq.test(COI_employment)$p.value,
  chisq.test(COI_advisory)$p.value,
  chisq.test(COI_honoraria)$p.value
)

print(p3_b)