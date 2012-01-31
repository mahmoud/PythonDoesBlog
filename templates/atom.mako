<%inherit file="feed_base.mako"/>
<%! 
  from datetime import datetime
  import settings 
%>
<%block name="body">
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:thr="http://purl.org/syndication/thread/1.0" xml:lang="en">
  <title type="text">${settings.BLOG_TITLE}</title>
  <subtitle type="text">${settings.BLOG_DESCRIPTION}</subtitle>

  <updated>${datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>

  <id>${settings.BLOG_URL}/feed/atom/</id>
  <link rel="self" type="application/atom+xml" href="${settings.BLOG_URL}feed/atom.xml" />
  <link rel="alternate" type="text/html" href="${settings.BLOG_URL}" />
  <generator uri="https://www.github.com/makuro/PythonDoesBlog">PythonDoesBlog</generator>

  % for post in posts:
  <entry>
    <author>
      <name>${post.author}</name>
      <uri>${settings.BLOG_URL}</uri>
    </author>
    <title type="html"><![CDATA[${post.title}]]></title>
    <link rel="alternate" type="text/html" href="${post.get_url(absolute=True)}" />
    <id>${post.id}</id>

    <published>${post.pub_date.strftime("%Y-%m-%dT%H:%M:%SZ")}</published>
    <updated>${post.updated.strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>

    % for tag in post.tags:
      <category scheme="${settings.BLOG_URL}tags/" term="${tag}" label="${tag.capitalize()}" />
    % endfor

    <summary type="html"><![CDATA[${post.title}]]></summary>
    <content type="html" xml:base="${post.get_url(absolute=True)}">
      <![CDATA[${self.absolutify(post.get_html(content_only=True, noclasses=True))}]]>
    </content>
  </entry>
% endfor
</feed>
</%block>
