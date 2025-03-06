library(dplyr)

data = analysis_dataset

data$publication_date = as.Date(data$publication_date)

group_1_start <- as.Date("2010-01-01")
group_1_end <- as.Date("2015-01-01")
group_2_start <- as.Date("2015-01-02")
group_2_end <- as.Date("2020-01-01")
group_3_start <- as.Date("2020-01-02")
group_3_end <- as.Date("2025-01-01")

data = data %>%
  mutate(
    group = case_when(
      publication_date >= group_1_start & publication_date <= group_1_end ~ "Group 1",
      publication_date >= group_2_start & publication_date <= group_2_end ~ "Group 2",
      publication_date >= group_3_start & publication_date <= group_3_end ~ "Group 3",
      TRUE ~ "Outside range"
    )
  )

data_involves_product = data %>% filter(!is.na(product_name))
write.csv(data_involves_product, "data_involves_product.csv", row.names = FALSE)

summary_table <- data_involves_product %>%
  group_by(group) %>%
  summarize(
    total_records = n(),
    true_count_in_company_list = sum(company_in_the_list == TRUE, na.rm = TRUE),
    percentage_true = (sum(company_in_the_list == TRUE, na.rm = TRUE) / n()) * 100
  )

print(summary_table)

# COI employment
summary_table_employment = data_involves_product %>%
  group_by(group) %>%
  summarize(
    total_records = n(),
    true_count_in_company_list = sum(coi_employment>0, na.rm = TRUE),
    percentage_true = (sum(coi_employment>0, na.rm = TRUE) / n()) * 100
  )
print (summary_table_employment)


# COI consulting
summary_table_consulting = data_involves_product %>%
  group_by(group) %>%
  summarize(
    total_records = n(),
    true_count_in_company_list = sum(coi_advisory_consulting>0, na.rm = TRUE),
    percentage_true = (sum(coi_advisory_consulting>0, na.rm = TRUE) / n()) * 100
  )
print (summary_table_consulting)

# for speakers bureau, will filter out records prior to 3/1/2015
speaker_bureau_data = data_involves_product %>%
  filter (publication_date>=as.Date("2015-03-01")) %>%
  mutate(
    group = case_when(
      publication_date >= group_1_start & publication_date <= group_1_end ~ "Group 1",
      publication_date >= group_2_start & publication_date <= group_2_end ~ "Group 2",
      publication_date >= group_3_start & publication_date <= group_3_end ~ "Group 3",
      TRUE ~ "Outside range"
      )
    )

summary_table_speakers_bureau = speaker_bureau_data %>%
  group_by(group) %>%
  summarize(
    total_records = n(),
    true_count_in_company_list = sum(coi_speakers_bureau>0, na.rm = TRUE),
    percentage_true = (sum(coi_speakers_bureau>0, na.rm = TRUE) / n()) * 100
  )
print (summary_table_speakers_bureau)


# COI honoraria
summary_table_honoraria = data_involves_product %>%
  group_by(group) %>%
  summarize(
    total_records = n(),
    true_count_in_company_list = sum(coi_honoraria>0, na.rm = TRUE),
    percentage_true = (sum(coi_honoraria>0, na.rm = TRUE) / n()) * 100
  )
print (summary_table_honoraria)



###############################################################
# AUTHOR NUMBERS
############################################################
# median IQR author numbers
author_no = data_involves_product %>%
  group_by(group) %>%
  summarise(
    median_authors = median(no_total_authors, na.rm = TRUE),
    Q1 = quantile(no_total_authors, 0.25, na.rm = TRUE),
    Q3 = quantile(no_total_authors, 0.75, na.rm = TRUE),
  )

print(author_no)

# median % of authors have COI
coi_author_percent = data_involves_product %>% 
  filter(no_author_with_any_coi>0) %>% 
  mutate(derived_value = no_author_with_any_coi / no_total_authors) %>% 
  summarize(
    median_percentage = median(derived_value, na.rm = TRUE) * 100, 
    Q1_percentage = quantile(derived_value, 0.25, na.rm = TRUE) * 100, 
    Q3_percentage = quantile(derived_value, 0.75, na.rm = TRUE) * 100  
  )
print(coi_author_percent)

coi_author_percent_grouped = data_involves_product %>% 
  filter(no_author_with_any_coi>0) %>% 
  mutate(derived_value = no_author_with_any_coi / no_total_authors) %>% 
  group_by(group) %>% 
  summarize(
    median_percentage = median(derived_value, na.rm = TRUE) * 100, 
    Q1_percentage = quantile(derived_value, 0.25, na.rm = TRUE) * 100, 
    Q3_percentage = quantile(derived_value, 0.75, na.rm = TRUE) * 100  
  )
print(coi_author_percent_grouped)

# median/IQR coi employment/total author in studies with emmployment COI
coi_percentage_employment = data_involves_product %>%
  filter(coi_employment>0, na.rm=TRUE) %>%
  mutate(derived_value = coi_employment / no_total_authors) %>% 
  group_by(group) %>%                                          
  summarize(
    median_percentage = median(derived_value, na.rm = TRUE) * 100, 
    Q1_percentage = quantile(derived_value, 0.25, na.rm = TRUE) * 100, 
    Q3_percentage = quantile(derived_value, 0.75, na.rm = TRUE) * 100  
  )

print(coi_percentage_employment)

# median/IQR coi advisory/total author in studies with advisory COI
coi_percentage_advisory = data_involves_product %>%
  filter(coi_advisory_consulting>0, na.rm=TRUE) %>%
  mutate(derived_value = coi_advisory_consulting / no_total_authors) %>% 
  group_by(group) %>%                                          
  summarize(
    median_percentage = median(derived_value, na.rm = TRUE) * 100, 
    Q1_percentage = quantile(derived_value, 0.25, na.rm = TRUE) * 100, 
    Q3_percentage = quantile(derived_value, 0.75, na.rm = TRUE) * 100  
  )

print(coi_percentage_advisory)

# median/IQR coi honoraria/total author in studies with honoraria COI
coi_percentage_honoraria = data_involves_product %>%
  filter(coi_honoraria>0, na.rm=TRUE) %>%
  mutate(derived_value = coi_honoraria / no_total_authors) %>% 
  group_by(group) %>%                                          
  summarize(
    median_percentage = median(derived_value, na.rm = TRUE) * 100, 
    Q1_percentage = quantile(derived_value, 0.25, na.rm = TRUE) * 100, 
    Q3_percentage = quantile(derived_value, 0.75, na.rm = TRUE) * 100  
  )

print(coi_percentage_honoraria)

################################
### top prodcuts
###############################

top_products = data_involves_product %>%
  group_by(group, product_name) %>%
  summarise(freq = n(), .groups = "drop") %>%
  group_by(group) %>%
  mutate(percentage = freq / sum(freq) * 100) %>%  # Calculate percentage
  arrange(group, desc(freq)) %>%
  slice_head(n = 3)
print(top_products)

############################
### phase of trials
##########################

library(stringr)

data = data_involves_product

categorize_phase <- function(title) {
  # Convert to uppercase for consistent matching
  title_upper <- toupper(title)
  
  # Define patterns for each phase category with variations
  phase_i_pattern <- "\\bPHASE I\\b|\\bPHASE 1\\b|\\bPHASE IA\\b|\\bPHASE IB\\b|\\bPHASE I/II\\b|\\bPHASE I/2\\b|\\bPHASE 1/II\\b|\\bPHASE 1/2\\b"
  phase_ii_pattern <- "\\bPHASE II\\b|\\bPHASE 2\\b|\\bPHASE IIA\\b|\\bPHASE IIB\\b|\\bPHASE II/III\\b|\\bPHASE II/3\\b|\\bPHASE 2/III\\b|\\bPHASE 2/3\\b"
  phase_iii_pattern <- "\\bPHASE III\\b|\\bPHASE 3\\b|\\bPHASE IIIA\\b|\\bPHASE IIIB\\b"
  
  # Check for each phase category
  phase_i <- str_detect(title_upper, regex(phase_i_pattern))
  phase_ii <- str_detect(title_upper, regex(phase_ii_pattern))
  phase_iii <- str_detect(title_upper, regex(phase_iii_pattern))
  
  # Handle overlapping patterns (e.g., Phase I/II should count for both Phase I and Phase II)
  # No additional processing needed as we've included the overlapping patterns in each category
  
  return(list(phase_i = phase_i, phase_ii = phase_ii, phase_iii = phase_iii))
}

# Apply the categorization function to each title
phase_results <- lapply(data$title, categorize_phase)

# Extract results into data frame columns
data$contains_phase_i <- sapply(phase_results, function(x) x$phase_i)
data$contains_phase_ii <- sapply(phase_results, function(x) x$phase_ii)
data$contains_phase_iii <- sapply(phase_results, function(x) x$phase_iii)

# Group by the 'group' variable and count occurrences of each phase
phase_counts <- data %>%
  group_by(group) %>%
  summarise(
    total_titles = n(),
    phase_i_count = sum(contains_phase_i, na.rm = TRUE),
    phase_ii_count = sum(contains_phase_ii, na.rm = TRUE),
    phase_iii_count = sum(contains_phase_iii, na.rm = TRUE),
    phase_i_percent = round(phase_i_count / total_titles * 100, 1),
    phase_ii_percent = round(phase_ii_count / total_titles * 100, 1),
    phase_iii_percent = round(phase_iii_count / total_titles * 100, 1)
  )

# Print the results
print(phase_counts)

##########################################
### countries
########################################

top_countries <- data_involves_product %>%
  group_by(group, main_country) %>%
  summarise(freq = n(), .groups = "drop") %>%
  group_by(group) %>%
  mutate(percentage = freq / sum(freq) * 100) %>%  # Calculate percentage
  arrange(group, desc(freq)) %>%
  slice_head(n = 15)
print(top_countries)

multi_nation_study = data_involves_product%>%
  group_by(group)%>%
  summarize(
    total_records = n(),
    multi_nation = sum(multiple_nationality>0, na.rm = T),
    percentage = multi_nation/total_records * 100)
print (multi_nation_study)

# COI by countries
US_based_study = data_involves_product%>%
  group_by(group)%>%
  summarize(
    total_records = n(),
    US_based = sum (main_country=='USA', na.rm=T), 
    percentage = US_based/total_records * 100)
print (US_based_study)


top_10_countries <- data_involves_product %>%
  group_by(main_country) %>%
  summarize(count = n(), .groups = "drop") %>%
  arrange(desc(count)) %>%
  slice_head(n = 10) %>%
  summarise(top_10_countries = paste(main_country, collapse = ", "))
print (top_10_countries)

top_countries_by_group <- data_involves_product %>%
  group_by(group, main_country) %>%
  summarize(count = n(), .groups = "drop") %>%
  arrange(group, desc(count)) %>%
  group_by(group) %>%
  slice_head(n = 3) %>%
  summarise(top_countries_by_group = paste(main_country, collapse = ", "))
print (top_countries_by_group)

# COI only in US
US_COI = data_involves_product%>%
  filter(main_country=='USA', na.rm=TRUE) %>%
  group_by(group) %>%
  summarize(
    total_records = n(),
    US_COI = sum(company_in_the_list==T, na.rm = TRUE),
    percentage_US_COI = (US_COI / n()) * 100
  )
print (US_COI)

# COI employment in US
US_COI_employment = data_involves_product%>%
  filter(main_country=='USA', na.rm=TRUE) %>%
  group_by(group) %>%
  summarize(
    total_records = n(),
    US_COI = sum(coi_employment>0, na.rm = TRUE),
    percentage_US_COI = (US_COI / n()) * 100
  )
print (US_COI_employment)

# COI advisory in US
US_COI_advisory = data_involves_product%>%
  filter(main_country=='USA', na.rm=TRUE) %>%
  group_by(group) %>%
  summarize(
    total_records = n(),
    US_COI = sum(coi_advisory_consulting>0, na.rm = TRUE),
    percentage_US_COI = (US_COI / n()) * 100
  )
print (US_COI_advisory)

# COI honoraria in US
US_COI_honoraria = data_involves_product%>%
  filter(main_country=='USA', na.rm=TRUE) %>%
  group_by(group) %>%
  summarize(
    total_records = n(),
    US_COI = sum(coi_honoraria>0, na.rm = TRUE),
    percentage_US_COI = (US_COI / n()) * 100
  )
print (US_COI_honoraria)

# COI for US - total
US_COI = data_involves_product %>%
  filter(main_country=='USA', na.rm=TRUE) %>%
  summarize (
    total_records = n(),
    COI_all = sum(company_in_the_list==T, na.rm=TRUE),
    COI_employment = sum(coi_employment>0, na.rm = TRUE),
    COI_advisory = sum(coi_advisory_consulting>0, na.rm = TRUE),
    percent_COI_all = COI_all / n() * 100,
    percent_employment = COI_employment / n() * 100, 
    percent_advisory = COI_advisory / n() * 100
  )
print (US_COI)

# COI only in non-US
non_US_COI = data_involves_product%>%
  filter(main_country!='USA', na.rm=TRUE) %>%
  group_by(group) %>%
  summarize(
    total_records = n(),
    US_COI = sum(company_in_the_list==T, na.rm = TRUE),
    percentage_US_COI = (US_COI / n()) * 100
  )
print (non_US_COI)

# COI employment in non-US
non_US_COI_employment = data_involves_product%>%
  filter(main_country!='USA', na.rm=TRUE) %>%
  group_by(group) %>%
  summarize(
    total_records = n(),
    US_COI = sum(coi_employment>0, na.rm = TRUE),
    percentage_US_COI = (US_COI / n()) * 100
  )
print (non_US_COI_employment)

# COI advisory in non-US
non_US_COI_advisory = data_involves_product%>%
  filter(main_country!='USA', na.rm=TRUE) %>%
  group_by(group) %>%
  summarize(
    total_records = n(),
    US_COI = sum(coi_advisory_consulting>0, na.rm = TRUE),
    percentage_US_COI = (US_COI / n()) * 100
  )
print (non_US_COI_advisory)

# COI honoraria in non-US
non_US_COI_honoraria = data_involves_product%>%
  filter(main_country!='USA', na.rm=TRUE) %>%
  group_by(group) %>%
  summarize(
    total_records = n(),
    US_COI = sum(coi_honoraria>0, na.rm = TRUE),
    percentage_US_COI = (US_COI / n()) * 100
  )
print (non_US_COI_honoraria)

# COI for non-US - total
non_US_COI = data_involves_product %>%
  filter(main_country!='USA', na.rm=TRUE) %>%
  summarize (
    total_records = n(),
    COI_all = sum(company_in_the_list==T, na.rm=TRUE),
    COI_employment = sum(coi_employment>0, na.rm = TRUE),
    COI_advisory = sum(coi_advisory_consulting>0, na.rm = TRUE),
    COI_honoraria = sum(coi_honoraria>0, na.rm = TRUE),
    percent_COI_all = COI_all / n() * 100,
    percent_employment = COI_employment / n() * 100, 
    percent_advisory = COI_advisory / n() * 100,
    percent_honoraria = COI_honoraria / n() * 100,
  )
print (non_US_COI)

# COI for Germany
Germany_COI = data_involves_product %>%
  filter(main_country=='Germany', na.rm=TRUE) %>%
  summarize (
    total_records = n(),
    COI_all = sum(company_in_the_list==T, na.rm=TRUE),
    COI_employment = sum(coi_employment>0, na.rm = TRUE),
    COI_advisory = sum(coi_advisory_consulting>0, na.rm = TRUE),
    percent_COI_all = COI_all / n() * 100,
    percent_employment = COI_employment / n() * 100, 
    percent_advisory = COI_advisory / n() * 100
  )
print (Germany_COI)

# COI for UK
UK_COI = data_involves_product %>%
  filter(main_country=='United Kingdom', na.rm=TRUE) %>%
  summarize (
    total_records = n(),
    COI_all = sum(company_in_the_list==T, na.rm=TRUE),
    COI_employment = sum(coi_employment>0, na.rm = TRUE),
    COI_advisory = sum(coi_advisory_consulting>0, na.rm = TRUE),
    percent_COI_all = COI_all / n() * 100,
    percent_employment = COI_employment / n() * 100, 
    percent_advisory = COI_advisory / n() * 100
  )
print (UK_COI)

# COI for France
France_COI = data_involves_product %>%
  filter(main_country=='France', na.rm=TRUE) %>%
  summarize (
    total_records = n(),
    COI_all = sum(company_in_the_list==T, na.rm=TRUE),
    COI_employment = sum(coi_employment>0, na.rm = TRUE),
    COI_advisory = sum(coi_advisory_consulting>0, na.rm = TRUE),
    percent_COI_all = COI_all / n() * 100,
    percent_employment = COI_employment / n() * 100, 
    percent_advisory = COI_advisory / n() * 100
  )
print (France_COI)

# COI for Italy
Italy_COI = data_involves_product %>%
  filter(main_country=='Italy', na.rm=TRUE) %>%
  summarize (
    total_records = n(),
    COI_all = sum(company_in_the_list==T, na.rm=TRUE),
    COI_employment = sum(coi_employment>0, na.rm = TRUE),
    COI_advisory = sum(coi_advisory_consulting>0, na.rm = TRUE),
    percent_COI_all = COI_all / n() * 100,
    percent_employment = COI_employment / n() * 100, 
    percent_advisory = COI_advisory / n() * 100
  )
print (Italy_COI)

# COI for China
China_COI = data_involves_product %>%
  filter(main_country=='China', na.rm=TRUE) %>%
  summarize (
    total_records = n(),
    COI_all = sum(company_in_the_list==T, na.rm=TRUE),
    COI_employment = sum(coi_employment>0, na.rm = TRUE),
    COI_advisory = sum(coi_advisory_consulting>0, na.rm = TRUE),
    percent_COI_all = COI_all / n() * 100,
    percent_employment = COI_employment / n() * 100, 
    percent_advisory = COI_advisory / n() * 100
  )
print (China_COI)


#####################################################
## first and last authors
####################################################
coi_first_or_last_author = data_involves_product %>%
  group_by(group) %>%
  summarize (
    total_records = n(),
    coi_n = sum (first_author_coi_all>0 | last_author_coi_all>0, na.rm = TRUE),
    percent = coi_n / n() * 100
  )
print (coi_first_or_last_author)

coi_employment_first_or_last_author = data_involves_product %>%
  group_by(group) %>% 
  summarize(
    total_n = n(),
    coi_n = sum (coi_employment_first_author>0 | coi_employment_last_author>0, na.rm=TRUE),
    percent = coi_n / total_n * 100
  )
print (coi_employment_first_or_last_author)

coi_advisory_first_or_last_author = data_involves_product %>%
  group_by(group) %>% 
  summarize(
    total_n = n(),
    coi_n = sum (coi_advisory_first_author>0 | coi_advisory_last_author>0, na.rm=TRUE),
    percent = coi_n / total_n * 100
  )
print (coi_advisory_first_or_last_author)

coi_speakers_first_or_last_author = data_involves_product %>%
  group_by(group) %>% 
  summarize(
    total_n = n(),
    coi_n = sum (coi_speakers_first_author>0 | coi_speakers_last_author>0, na.rm=TRUE),
    percent = coi_n / total_n * 100
  )
print (coi_speakers_first_or_last_author)

coi_honoraria_first_or_last_author = data_involves_product %>%
  group_by(group) %>% 
  summarize(
    total_n = n(),
    coi_n = sum (coi_honoraria_first_author>0 | coi_honoraria_last_author>0, na.rm=TRUE),
    percent = coi_n / total_n * 100
  )
print (coi_honoraria_first_or_last_author)