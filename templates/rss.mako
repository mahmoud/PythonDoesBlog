<%inherit file="feed_base.mako"/>
<%! 
  from datetime import datetime
  import settings 
%>
<%block name="body">
<rss version="2.0"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:sy="http://purl.org/rss/1.0/modules/syndication/"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     >
  <channel>
    <title>${settings.BLOG_TITLE}</title>
    <link>${settings.BLOG_URL}</link>
    <description>${settings.BLOG_DESCRIPTION}</description>
    <atom:link rel="self" type="application/rss+xml" href="${settings.BLOG_URL}feed/rss.xml" />

    % if settings.get("PUBSUB_URL"):
    <atom:link rel="hub" href="${settings.PUBSUB_URL}" />
    % endif

    <pubDate>${datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")}</pubDate>
    <sy:updatePeriod>hourly</sy:updatePeriod>
    <sy:updateFrequency>1</sy:updateFrequency>

    <generator>PythonDoesBlog</generator>

    % for post in posts:
    <item>
      <title><![CDATA[${post.title}]]></title>

      <pubDate>${post.pub_date.strftime("%a, %d %b %Y %H:%M:%S GMT")}</pubDate>

      % for tag in post.tags:
      <category><![CDATA[${tag}]]></category>
      % endfor

      <link>${post.get_url(absolute=True)}</link>
      <guid>${post.get_url(absolute=True)}</guid>

      <description>
	<![CDATA[${self.absolutify(post.get_html(content_only=True, noclasses=True))}]]>
      </description>
    </item>
    % endfor

  </channel>
</rss>
</%block>
