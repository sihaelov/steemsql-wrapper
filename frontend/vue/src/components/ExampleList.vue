<template>

  <div class="example-list">

    <div
    v-for="(item) in queries"
    v-bind:key="item.title"
    :class="`card valign-wrapper ${item.colorClasses}`"
    @click="setNewExampleCode(item.sql)">
      <p class="title">
        {{item.title}}
      </p>
      <div class="overlay valign-wrapper"><p>See query</p></div>
      <p class="raw-sql" :sql="item.sql"></p>
    </div>

    <!--
      SELECT * FROM sys.views
      select * from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='tableName'

      SELECT CONVERT(DATE, created), SUM(net_votes)
      FROM Comments
      WHERE created >= '2017/12/06' AND created < '2017/12/07'
      GROUP BY CONVERT(DATE, created)
      ORDER BY CONVERT(DATE, created)
    -->

  </div> <!--/.example-list -->

</template>

<script>


export default {
  name: 'ExampleList',
  data() {
    return {
      queries: [
        {
          title: 'Тоp 30 posts by number of upvotes',
          sql: "SELECT TOP 30&#10;author, category, net_votes, title, url&#10;FROM Comments&#10;WHERE parent_author='' AND created >= '{date}' AND created < '{nextDate}'&#10;ORDER BY net_votes DESC",
          colorClasses: 'orange lighten-1',
        },
        {
          title: 'Top 30 posts by number of comments',
          sql: "SELECT TOP 30&#10;author, category, children, title, url&#10;FROM Comments&#10;WHERE parent_author='' AND created >= '{date}' AND created < '{nextDate}'&#10;ORDER BY children DESC",
          colorClasses: 'deep-orange lighten-1',
        },
        {
          title: 'Top 30 posts by pending payout',
          sql: "SELECT TOP 30&#10;author, category, pending_payout_value, title, url&#10;FROM Comments&#10;WHERE parent_author='' AND created >= '{date}' AND created < '{nextDate}'&#10;ORDER BY pending_payout_value DESC",
          colorClasses: 'green lighten-1',
        },
        {
          title: 'Daily number of posts',
          sql: "SELECT CONVERT(DATE, created) as Date, COUNT(*) as Posts&#10;FROM Comments&#10;WHERE created >= '{dateWeekAgo}' AND created < '{date}'&#10;GROUP BY CONVERT(DATE, created)&#10;ORDER BY CONVERT(DATE, created) DESC",
          colorClasses: 'blue lighten-1',
        },
        {
          title: 'Daily number of new accounts',
          sql: "SELECT CONVERT(DATE, timestamp) as Date, COUNT(*) as [New Accounts]&#10;FROM TxAccountCreates&#10;WHERE timestamp >= '{dateWeekAgo}' AND timestamp < '{date}'&#10;GROUP BY CONVERT(DATE, timestamp)&#10;ORDER BY CONVERT(DATE, timestamp) DESC",
          colorClasses: 'purple lighten-1',
        },
        {
          title: 'Daily number of votes',
          sql: "SELECT CONVERT(DATE, timestamp) as Date, COUNT(*) as Votes&#10;FROM TxVotes&#10;WHERE timestamp >= '{dateWeekAgo}' AND timestamp < '{date}'&#10;GROUP BY CONVERT(DATE, timestamp)&#10;ORDER BY CONVERT(DATE, timestamp) DESC",
          colorClasses: 'indigo lighten-1',
        },
        {
          title: 'Top 50 utopian contributors by pending payout',
          sql: "SELECT TOP 50 author, SUM(pending_payout_value) as [Pending Payout]&#10;FROM Comments&#10;WHERE&#10;    parent_author='' AND&#10;    created >= '{dateWeekAgo}' AND&#10;    created < '{date}' AND&#10;    category='utopian-io'&#10;GROUP BY author&#10;ORDER BY SUM(pending_payout_value) DESC",
          colorClasses: 'red lighten-1',
        },
      ],
    };
  }, // data
  methods: {
    setNewExampleCode(sql) {
      this.$emit('setNewExampleCode', sql);
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
