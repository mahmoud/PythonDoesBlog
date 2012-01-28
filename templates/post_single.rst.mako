${post.title}
${ '-' * len(post.title) }

PDW#${post.id} - ${post.author} - ${post.pub_date}

${post.get_rst(noclasses=noclasses)}


% if post.tags:
Tagged under:

.. class:: tags

   % for tag in post.tags:
   - ${tag | h}
   % endfor

% endif



