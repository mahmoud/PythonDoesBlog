<%! import settings %>
${post.title}
${ '-' * len(post.title) }

% if settings.get('BREEV') and post.id:
${settings.BREEV} #${post.id} - ${post.author} - ${post.pub_date}
% else:
${post.author} - ${post.pub_date}
% endif

${post.get_rst(noclasses=noclasses)}


% if post.tags:
Tagged under:

.. class:: tags

   % for tag in post.tags:
   - ${tag | h}
   % endfor

% endif



