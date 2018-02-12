<template>
  <div id="app">
    <div class="main-content">

        <div class="db-schema">
            <div class="loader-wrapper">
                <div class="preloader-wrapper big active">
                    <div class="spinner-layer spinner-blue-only">
                      <div class="circle-clipper left">
                        <div class="circle"></div>
                      </div><div class="gap-patch">
                        <div class="circle"></div>
                      </div><div class="circle-clipper right">
                        <div class="circle"></div>
                      </div>
                    </div>
                </div>
            </div>

            <ul class="collapsible" data-collapsible="accordion" style="display: none;"></ul>
        </div>

        <div class="example-list">
    
          <div class="card valign-wrapper orange lighten-1">
              <p class="title">
                  Тоp 30 posts by number of upvotes
              </p>
              <div class="overlay valign-wrapper"><p>See query</p></div>
              <p class="raw-sql" sql="SELECT TOP 30&#10;author, category, net_votes, title, url&#10;FROM Comments&#10;WHERE parent_author='' AND created >= '${date}' AND created < '${nextDate}'&#10;ORDER BY net_votes DESC"></p>
          </div>

            <div class="card valign-wrapper deep-orange lighten-1">
                <p class="title">
                    Top 30 posts by number of comments
                </p>
                <div class="overlay valign-wrapper"><p>See query</p></div>
                <p class="raw-sql" sql="SELECT TOP 30&#10;author, category, children, title, url&#10;FROM Comments&#10;WHERE parent_author='' AND created >= '${date}' AND created < '${nextDate}'&#10;ORDER BY children DESC"></p>
            </div>

            <div class="card valign-wrapper green lighten-1">
                <p class="title">
                    Top 30 posts by pending payout
                </p>
                <div class="overlay valign-wrapper"><p>See query</p></div>
                <p class="raw-sql" sql="SELECT TOP 30&#10;author, category, pending_payout_value, title, url&#10;FROM Comments&#10;WHERE parent_author='' AND created >= '${date}' AND created < '${nextDate}'&#10;ORDER BY pending_payout_value DESC"></p>
            </div>

            <div class="card valign-wrapper blue lighten-1">
                <p class="title">
                    Daily number of posts
                </p>
                <div class="overlay valign-wrapper"><p>See query</p></div>
                <p class="raw-sql" sql="SELECT CONVERT(DATE, created) as Date, COUNT(*) as Posts&#10;FROM Comments&#10;WHERE created >= '${dateWeekAgo}' AND created < '${date}'&#10;GROUP BY CONVERT(DATE, created)&#10;ORDER BY CONVERT(DATE, created) DESC"></p>

            </div>

            <div class="card valign-wrapper purple lighten-1">
                <p class="title">
                    Daily number of new accounts
                </p>
                <div class="overlay valign-wrapper"><p>See query</p></div>
                <p class="raw-sql" sql="SELECT CONVERT(DATE, timestamp) as Date, COUNT(*) as [New Accounts]&#10;FROM TxAccountCreates&#10;WHERE timestamp >= '${dateWeekAgo}' AND timestamp < '${date}'&#10;GROUP BY CONVERT(DATE, timestamp)&#10;ORDER BY CONVERT(DATE, timestamp) DESC"></p>
            </div>

            <div class="card valign-wrapper indigo lighten-1">
                <p class="title">
                    Daily number of votes
                </p>
                <div class="overlay valign-wrapper"><p>See query</p></div>
                <p class="raw-sql" sql="SELECT CONVERT(DATE, timestamp) as Date, COUNT(*) as Votes&#10;FROM TxVotes&#10;WHERE timestamp >= '${dateWeekAgo}' AND timestamp < '${date}'&#10;GROUP BY CONVERT(DATE, timestamp)&#10;ORDER BY CONVERT(DATE, timestamp) DESC"></p>
            </div>

            <div class="card valign-wrapper red lighten-1">
                <p class="title">
                    Top 50 utopian contributors by pending payout
                </p>
                <div class="overlay valign-wrapper"><p>See query</p></div>
                <p class="raw-sql" sql="SELECT TOP 50 author, SUM(pending_payout_value) as [Pending Payout]&#10;FROM Comments&#10;WHERE&#10;    parent_author='' AND&#10;    created >= '${dateWeekAgo}' AND&#10;    created < '${date}' AND&#10;    category='utopian-io'&#10;GROUP BY author&#10;ORDER BY SUM(pending_payout_value) DESC"></p>
            </div>

          </div> <!--/.example-list -->

        
    </div> <!-- main-content -->
  </div>
</template>

<script>
export default {
  name: 'app',
  data () {
    return {
      msg: ''
    }
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

h1, h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}
</style>
