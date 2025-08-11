import scrapy


class JobItem(scrapy.Item):
    company = scrapy.Field()
    url = scrapy.Field()
    job_title = scrapy.Field()
    job_description = scrapy.Field()
    job_requirements = scrapy.Field()
    publish_date = scrapy.Field()  # str or date-like; will be normalized in pipeline
    deadline = scrapy.Field()      # str or date-like; will be normalized in pipeline
    education_requirement = scrapy.Field()

    # extra metadata
    company_size_category = scrapy.Field()  # big | medium | small | unknown
    source_site = scrapy.Field()
    city = scrapy.Field()