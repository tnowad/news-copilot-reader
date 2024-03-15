# SITE MAP

## PAGE(requirement) User: -> path: /user

### HomePage:

1. Information all news writer: path: /

- header : route switch between topics,...
- hot news paper of topic
- all news of topic
- footer: contact article author,social media,...

### DetailsNews,comment,like

2. Details of article: path: /DetailNews/{idArticle}

- header
- detail information of article:
  - content article
  - information main revolves around the article
- maybe add sidebar to show up tables of content
- comment and like
- footer

### SignIn and SignOut:

3. Sign In and Sign Out(support social media: facebook,github,google): path: /SignIn and /SignOut

- header
- if user just read article -> no need sign in sign up
- else user want to write,suply information relate to article -> must sign in, sign up
- footer

### WriteNews:

4. Support to write news: path /writeNews/{idUser}

- header
- selection topic to write news
- authenticating the news source
- source news
- submit and wait to approve
- footer

## PAGE(requirement) Admin: -> path: /admin

### HomeAdmin:

1. allow post approval: path: /approve/{idUser}

- header
- table list all post news wait to approve:
  - button approve switch status post news
- footer

### Management user:

2. management user(Delete user and Edit user): path: /mamagementUser/{idUser}

- header
- table list all user need to manage:
  - button delete and edit -> form edit and authentication section deletes the user
- footer

### Report:

3. statistical reports on views and reports on users: path: /report

- header
- table statistical reports about numnber of views
- table reports account of user and reports about some articles negative

## PAGE(optional) user: /user

### postCast and radio:

1. switch from text to voice postcast and connect radio waves

- header
- navber between postcast and radio:
  - postcast: show up all postcast: path: /postcast
  - radio: support scan on waves radio: path: /radio
- footer

## ALL FUNCTIONS:

1. Sign in,Sign out be supported by account facebook,google,git hub,...
2. Forget Password
3. Write news support AI train model generate text
4. Switch from text to voice support for radio and postcast
5. CRUD news,users
6. comments,like,reports news
7. allow post news approval
8. authentication
9. bookmark
10. data analysis about user behavior by read news history
