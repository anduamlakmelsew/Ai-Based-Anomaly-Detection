from urllib.parse import urlparse, urljoin, parse_qs


def validate_url(url):
    """
    Validate if URL is correct
    """

    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def normalize_url(base, link):
    """
    Convert relative URL to absolute URL
    """

    return urljoin(base, link)


def extract_parameters(url):
    """
    Extract query parameters from URL
    """

    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    return params


def remove_fragment(url):
    """
    Remove # fragments from URLs
    """

    parsed = urlparse(url)

    return parsed.scheme + "://" + parsed.netloc + parsed.path


def is_same_domain(base, target):
    """
    Check if target belongs to same domain
    """

    base_domain = urlparse(base).netloc
    target_domain = urlparse(target).netloc

    return base_domain == target_domain


def unique_urls(urls):
    """
    Remove duplicate URLs
    """

    return list(set(urls))