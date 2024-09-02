from flask import Flask, request, jsonify, send_file
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)

# Function to analyze SEO elements of a given URL
def analyze_seo(url, keyword=None):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Meta tags analysis
        title = soup.find('title').string if soup.find('title') else "Missing"
        description = soup.find('meta', attrs={'name': 'description'})
        description = description['content'] if description else "Missing"

        # Broken links analysis
        broken_links = []
        links = soup.find_all('a')
        for link in links:
            href = link.get('href')
            if href and not href.startswith('#') and not href.startswith('mailto:'):
                try:
                    link_response = requests.get(href)
                    if link_response.status_code == 404:
                        broken_links.append(href)
                except:
                    broken_links.append(href)

        # Heading tags analysis
        headings = analyze_headings(soup)

        # Image alt tags analysis
        missing_alts = analyze_images(soup)

        # Canonical link check
        canonical_link = analyze_canonical(soup)

        # Robots.txt and Sitemap.xml checks
        has_robots_txt = check_robots_txt(url)
        has_sitemap_xml = check_sitemap_xml(url)

        # Mobile-friendliness check
        mobile_friendly = analyze_mobile_friendly(soup)

        # Content length analysis
        content_length = analyze_content_length(soup)

        # Additional functionalities
        internal_external_links = analyze_links(soup, url)
        favicon_present = check_favicon(soup)
        large_images = analyze_image_sizes(soup)
        inline_css_js = check_inline_css_js(soup)
        text_html_ratio = calculate_text_html_ratio(soup)
        word_count = analyze_word_count(soup)
        duplicate_meta_tags = check_duplicate_meta_tags(soup)
        anchor_text_analysis = analyze_anchor_text(soup)
        image_dimensions_check = check_image_dimensions(soup)

        # Keyword analysis
        keyword_analysis = analyze_keyword(soup, keyword) if keyword else {}

        return {
            'title': title,
            'description': description,
            'broken_links': broken_links,
            'headings': headings,
            'missing_alts': missing_alts,
            'canonical_link': canonical_link,
            'has_robots_txt': has_robots_txt,
            'has_sitemap_xml': has_sitemap_xml,
            'mobile_friendly': mobile_friendly,
            'content_length': content_length,
            'internal_external_links': internal_external_links,
            'favicon_present': favicon_present,
            'large_images': large_images,
            'inline_css_js': inline_css_js,
            'text_html_ratio': text_html_ratio,
            'word_count': word_count,
            'duplicate_meta_tags': duplicate_meta_tags,
            'anchor_text_analysis': anchor_text_analysis,
            'image_dimensions_check': image_dimensions_check,
            'keyword_analysis': keyword_analysis  # Add keyword analysis results
        }

    except Exception as e:
        return {'error': str(e)}

# Additional SEO analysis functions

def analyze_headings(soup):
    headings = {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0}
    for level in headings.keys():
        headings[level] = len(soup.find_all(level))
    return headings

def analyze_images(soup):
    images = soup.find_all('img')
    missing_alt = [img['src'] for img in images if not img.get('alt')]
    return missing_alt

def analyze_canonical(soup):
    canonical = soup.find('link', rel='canonical')
    return canonical['href'] if canonical else 'Missing'

def check_robots_txt(url):
    robots_url = url.rstrip('/') + '/robots.txt'
    response = requests.get(robots_url)
    return response.status_code == 200

def check_sitemap_xml(url):
    sitemap_url = url.rstrip('/') + '/sitemap.xml'
    response = requests.get(sitemap_url)
    return response.status_code == 200

def analyze_mobile_friendly(soup):
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    return 'Present' if viewport else 'Missing'

def analyze_content_length(soup):
    text = soup.get_text(strip=True)
    return len(text)

# New functionalities

def analyze_links(soup, url):
    internal_links = 0
    external_links = 0
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith(url):
            internal_links += 1
        else:
            external_links += 1
    return {'internal_links': internal_links, 'external_links': external_links}

def check_favicon(soup):
    favicon = soup.find('link', rel='icon')
    return 'Present' if favicon else 'Missing'

def analyze_image_sizes(soup):
    large_images = []
    for img in soup.find_all('img'):
        try:
            src = img['src']
            img_response = requests.get(src, stream=True)
            if int(img_response.headers.get('Content-Length', 0)) > 100 * 1024:  # 100 KB
                large_images.append(src)
        except:
            continue
    return large_images

def check_inline_css_js(soup):
    inline_css_js = {'inline_css': False, 'inline_js': False}
    if soup.find_all('style'):
        inline_css_js['inline_css'] = True
    if soup.find_all('script'):
        inline_css_js['inline_js'] = True
    return inline_css_js

def calculate_text_html_ratio(soup):
    text = soup.get_text(strip=True)
    html = str(soup)
    return len(text) / len(html) if len(html) > 0 else 0

def analyze_word_count(soup):
    text = soup.get_text(strip=True)
    return len(text.split())

def check_duplicate_meta_tags(soup):
    meta_tags = [meta.attrs['name'] for meta in soup.find_all('meta') if 'name' in meta.attrs]
    return {tag: meta_tags.count(tag) for tag in set(meta_tags) if meta_tags.count(tag) > 1}

def analyze_anchor_text(soup):
    anchors = [a.get_text(strip=True) for a in soup.find_all('a')]
    return anchors

def check_image_dimensions(soup):
    images_without_dimensions = []
    for img in soup.find_all('img'):
        if not img.get('width') or not img.get('height'):
            images_without_dimensions.append(img['src'])
    return images_without_dimensions

# Keyword analysis function
def analyze_keyword(soup, keyword):
    if not keyword:
        return {}

    keyword = keyword.lower()
    keyword_analysis = {}

    # Title Tag
    title = soup.find('title').string.lower() if soup.find('title') else ""
    keyword_analysis['title_contains'] = keyword in title

    # Meta Description
    description = soup.find('meta', attrs={'name': 'description'})
    description_content = description['content'].lower() if description else ""
    keyword_analysis['description_contains'] = keyword in description_content

    # Headings
    keyword_analysis['headings_contain'] = {
        'h1': keyword_in_headings(soup, 'h1', keyword),
        'h2': keyword_in_headings(soup, 'h2', keyword),
        'h3': keyword_in_headings(soup, 'h3', keyword),
    }

    # Content
    text = soup.get_text(strip=True).lower()
    keyword_analysis['content_contains'] = keyword in text
    keyword_analysis['keyword_density'] = calculate_keyword_density(text, keyword)

    return keyword_analysis

def keyword_in_headings(soup, tag, keyword):
    headings = soup.find_all(tag)
    return any(keyword in heading.get_text(strip=True).lower() for heading in headings)

def calculate_keyword_density(text, keyword):
    word_count = len(text.split())
    keyword_count = text.split().count(keyword)
    return (keyword_count / word_count) * 100 if word_count > 0 else 0

# Route for the homepage
@app.route('/')
def index():
    return send_file('index.html')

# Route for performing the SEO analysis
@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form.get('url')
    keyword = request.form.get('keyword')
    if not url.startswith('http'):
        url = 'http://' + url

    result = analyze_seo(url, keyword)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
