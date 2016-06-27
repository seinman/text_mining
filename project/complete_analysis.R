if (!require("dplyr")) install.packages("dplyr"); library(dplyr)
if (!require("rjson")) install.packages("rjson"); library(rjson)
if (!require("stringr")) install.packages("stringr"); library(stringr)
wd <- 'scraped_data/metadata'
setwd(wd)

# LOAD IN THE 58109 DATA
debate_58109 <- fromJSON(file = 'all_debates_0_1000' )
debate2_58109 <- fromJSON(file = 'all_debates')
gender_58109 <- fromJSON(file = 'genders')

# LOAD IN THE 1971 DATA
lda_data <- fromJSON(file = 'forLDA0_1000')
lda_data2 <- fromJSON(file = 'forLDA')
topic_1971 <- fromJSON(file = 'topiclist')
all_urls_1971 <- c(sapply(lda_data, function(x) return(x[[1]])), sapply(lda_data2, function(x) return(x[[1]])))

# PUT THEM TOGETHER
all_data_58109 <- data.frame(gender = gender_58109, 
                             titles = c(debate_58109[[1]], debate2_58109[[1]]),
                             sentiment = c(debate_58109[[2]], debate2_58109[[2]]),
                             nwords = c(debate_58109[[5]], debate2_58109[[5]]),
                             url = c(debate_58109[[7]], debate2_58109[[7]]),
                             member = c(debate_58109[[6]], debate2_58109[[6]]))
all_data_1971 <- data.frame(topic = topic_1971,
                            url = all_urls_1971)
all_data <- left_join(all_data_58109, all_data_1971)
# get rid of unknown topics
all_data <- filter(all_data, topic != '999')

################################################
# FIGURE OUT WHO'S IN WHICH PARTY
party_info <- read.csv('mps.csv', stringsAsFactors = FALSE)
all_mp_names <- as.character(unique(all_data$member))
all_parties <- rep("Unknown", length(all_mp_names))
for(mp in all_mp_names) {
  cat(sum(is.na(all_parties)))
  cat(mp)
  cat('..')
  #cat(mp)
  cat('1')
  cat(',,')
  which_in <- sapply(party_info$Last.name, str_detect, string = mp)
  # If there's only one person with a certain surname, attach their party
  if(sum(which_in) == 1) {
    all_parties[all_mp_names == mp] <- party_info$Party[which_in]
  }
  # If there's two or more, look at the first name
  else if(sum(which_in) > 1) {
    which_in2 <- sapply(party_info$First.name, str_detect, string = mp)
    # If there's only one with the same first and surname, attach their party
    if(sum(which_in & which_in2) == 1) {
      all_parties[all_mp_names == mp] <- party_info$Party[which_in & which_in2]      
    }
  }
  if(all_parties[all_mp_names == mp] == 'Unknown') {
    if(str_detect(mp, '(Lab)')) {
      cat('k')
      all_parties[all_mp_names == mp] <- "Labour"
    }
    else if(str_detect(mp, '(Con)')) {
      all_parties[all_mp_names == mp] <- 'Conservative'
    }
    else if(str_detect(mp, '(SNP)')) {
      all_parties[all_mp_names == mp] <- 'Scottish National Party'
    }
    else if(str_detect(mp, '(DUP)')) {
      all_parties[all_mp_names == mp] <- 'DUP'
    }
    else if(str_detect(mp, '(PC)')) {
      all_parties[all_mp_names == mp] <- 'Plaid Cymru'
    }
  }
}

# Fill in the ones that are as yet undone
for(mp in c('The Prime Minister', 'Mr Hammond', 'Mr Allen','John Stevenson', 'Mrs Grant', 'Mr Walker', 'The First Deputy Chairman',
            'The Deputy Leader of the House of Commons (Dr Thérèse Coffey)', 'Dr Coffey', 'Dr Thérèse Coffey', 'The Solicitor General', 'Mr Cox',
            'The Attorney General', 'Dr Davies', 'Karl M<U+1D9C>Cartney', 'Mr Clarke', 'Gareth Johnson', 'Mr Rees-Mogg',
            'Mr Duncan Smith', 'Dr Lewis', 'Huw Irranca-Davies')) {
  all_parties[all_mp_names == mp] <- "Conservative"
}
  
for(mp in c('John McDonnell', 'Mrs Murray', 'Mr Reed', 'Mrs Lewell-Buck', 'Mr Cunningham', 'Dr Whitehead', 'Ms Stuart', 
            'Mr Nicholas Brown', 'Dr Blackman-Woods', 'Mr Mahmood')) {
  all_parties[all_mp_names == mp] <- "Labour"
}  

for(mp in c('Dr Whiteford', 'Dr Cameron', 'Dr Monaghan', "Brendan O'Hara", "John Mc Nally")) {
  all_parties[all_mp_names == mp] <- "Scottish National Party"
}

all_parties[str_detect(all_mp_names, 'Liz Saville Roberts')] <- "Plaid Cymru"

all_parties[all_mp_names == 'Ian Paisley'] <- "DUP"
all_parties[all_mp_names == "Dr McDonnell"] <- "Social Democratic and Labour"

d <- data.frame(party = all_parties, member = all_mp_names)

#################################################################
# FINAL FEW LINES OF CODE
###################################################################

all_data <- left_join(d, all_data)
# This happens because Reasons
all_data$topic <- as.integer(all_data$topic)

all_topics <- sort(unique(all_data$topic))
sentiment_results <- matrix(NA, ncol = 4, nrow = length(all_topics))
nwords_results <- matrix(NA, ncol = 4, nrow = length(all_topics))

iterator <- 1
for(topic in all_topics) {
  m <- lm(sentiment ~ gender + party, data = all_data[all_data$topic == topic,])
  sentiment_results[iterator,] <- summary(m)$coefficients[2,]
  m2 <- lm(nwords ~ gender + party, data = all_data[all_data$topic == topic,])
  nwords_results[iterator,] <- summary(m2)$coefficients[2,]
  iterator <- iterator + 1
}

final_results <- data.frame(nobs = table(all_data$topic), topic = all_topics, sent = sentiment_results, nwords = nwords_results)

sentiment_results <- cbind(1:30, sentiment_results)
colnames(sentiment_results) <- c('Topic', 'Estimate', 'Std. Error', 't value', 'p value')

nwords_results <- cbind(1:30, nwords_results)
colnames(nwords_results) <- c('Topic', 'Estimate', 'Std. Error', 't value', 'p value')


