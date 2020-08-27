# Data Collection Process

Data used for this project is not available publicly. The original data included two files: wp_post.json, containing content from a small science news website, and analytics2020.csv, containing year-to-date traffic analytics associated with the content. 

wp_post.json was obtained by exporting the results of the following MySQL query in JSON format:

`SELECT post_name, post_title, post_content
FROM wp_posts
WHERE post_type = 'post' AND post_status = 'publish'`

analytics2020.csv was obtained by exporting YTD Google Analytics data in CSV format. 