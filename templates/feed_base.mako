<?xml version="1.0" encoding="UTF-8"?>
<%! 
  from datetime import datetime
  import settings 
%>
<%def name="absolutify(link_or_text)">
    <%
       if not link_or_text:
           ret = link_or_text
       elif link_or_text[0] == '/':
           ret = settings.BLOG_URL + link_or_text
       else:
           ret = link_or_text.replace('href="/', 'href="'+settings.BLOG_URL)

       return ret
    %>
</%def>
${next.body()}