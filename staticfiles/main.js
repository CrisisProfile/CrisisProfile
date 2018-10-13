$(function() {
  Vue.component('checklist-instance-item', {
    delimiters: ["{(", ")}"],
  template: '\
    <li>\
      <input type="checkbox" /> {( title )} \
      <template v-if="!is_checked"><strong>Reason for not doing it:</strong> <input type="text" /></template>\
    </li>\
  ',
  props: ['title', 'is_checked']
  })
  Vue.component('checklist-instance', {
    delimiters: ["{(", ")}"],
  template: '<div><h5>{( name )}</h5>\
  <ol>\
  <checklist-instance-item v-bind:title="item" v-bind:is_checked="false" v-for="item in items"></checklist-instance-item>\
  </ol>\
  </div>\
  ',
  props: ['name', 'items']
  })
  Vue.component('checklist-creation-item', {
    delimiters: ["{(", ")}"],
  template: '\
    <li>\
      {( title )}\
      <button v-on:click="$emit(\'remove\')">Remove</button>\
    </li>\
  ',
  props: ['title']
})
Vue.component('checklists', {
  delimiters: ["{(", ")}"],
  data: function () {
    return {}},
    computed: {
      dailyChecklists: function() {

              if (!('definitions' in this.checklists)) {
                return []
              }
              dailyChecklists = [];
              for (var i=0;i <this.checklists['definitions'].length;i++) {
                console.log(this.checklists['definitions'][i]['triggers'])
                if ('triggers' in this.checklists['definitions'][i]) {
                if (this.checklists['definitions'][i]['triggers'].indexOf('daily') > -1) {
                  dailyChecklists.push(this.checklists['definitions'][i])
}
                }
              }
              return dailyChecklists;

      }
    },
  template: '<div><h4>Create new checklist</h4>\
  <create-checklist>\
  </create-checklist>\
  <h4>Daily Checklists</h4>\
<checklist-instance v-bind:name="instance.name" v-bind:items="instance.items" v-for="instance in dailyChecklists"></checklist-instance>\
  </div>',
  props: ['checklists'],
  methods: {
  },
  created:function() {
},


})
Vue.component('create-checklist', {
  delimiters: ["{(", ")}"],
  data: function () {
    return {
      name: '',
      newTodoText: '', todos: [], nextTodoId: 0,
      triggers: [{'is_checked': false, 'trigger': 'daily'}]
    }
  },
  methods: {
    createChecklist: function() {

      items = [];
      for (i=0;i<this.todos.length;i++) {
        items.push(this.todos[i]['title'])
      }
      triggers = [];
      for (i=0;i<this.triggers.length;i++) {
        if (this.triggers[i]['is_checked']) {           triggers.push(this.triggers[i]['trigger'])
      }
      }
      urlParts = {name: this.name, items: JSON.stringify(items), triggers: JSON.stringify(triggers)}
      console.log(urlParts);
      this.name = '';
      this.newTodoText = '';
      this.todos = [];
      this.nextTodoId = 0;

      $.post('/api/create_checklist', urlParts, function(data) {
console.log(JSON.stringify(data))
      })
    },
    addNewTodo: function () {
      this.todos.push({
        id: this.nextTodoId++,
        title: this.newTodoText
      })
      this.newTodoText = ''
    }
  },
  template: '<div><strong>Name:</strong> <input v-model="name" />\ <strong>Items:</strong>\
    <form v-on:submit.prevent="addNewTodo">\
      <label for="new-todo" @keyup.enter="addNewTodo">Add an item</label>\
      <input\
        v-model="newTodoText"\
        id="new-todo"\
      >\
      <button>Add</button>\
    </form>\
    <ol>\
      <li\
        is="checklist-creation-item"\
        v-for="(todo, index) in todos"\
        v-bind:key="todo.id"\
        v-bind:title="todo.title"\
        v-on:remove="todos.splice(index, 1)"\
      ></li>\
    </ol>\
    <strong>Triggers:</strong> <ul><li v-for="trigger in triggers">\
    <input type="checkbox" v-model="trigger.is_checked"/> <input v-model="trigger.trigger"></li></ul>\
    <button v-on:click="createChecklist">Save</button></div>',

})
Vue.component('thought', {
  delimiters: ["{(", ")}"],
  computed: {formattedTime: function() {
    return moment(this.datetime).format()
  },autoresponse: function() {
    return '<strong>Automatic response:</strong> '+ this.linkify(this.automatic_response)
  },linkified_thought: function() {
    return this.linkify(this.thought)
  }},
template: '\
  <li>\
    <strong>{( formattedTime )}:</strong> <span v-html="linkified_thought"></span>\
    <span v-if="automatic_response" v-html="autoresponse"> </span>\
  </li>\
',
props: ['thought', 'datetime', 'automatic_response'],
methods: {
  'linkify': function(text) {
    return linkifyHtml(text, {
  defaultProtocol: 'https'
});
  }
}
})
Vue.component('thoughts', {
  delimiters: ["{(", ")}"],
  data: function() {
    return {'thought': ''}
  },
template: '\
  <div>\
    <h3>Thoughts</h3>\
    <input type="text" v-model="thought" @keyup.enter="save" style="width:100%;" placeholder="thought"/>\
    <button v-on:click="save">Save</button>\
    <ul>\
    <thought v-for="thought in thoughts" :key="thought.datetime" v-bind:thought="thought.thought" v-bind:datetime="thought.datetime" v-bind:automatic_response="thought.automatic_response"></thought></ul>\
  </div>\
',
methods: {
  save: function() {

    $.post('/api/save_thought', {'thought': this.thought}, function(data) {
      app.thoughts = data;

    })
    this.thought = '';
  }
},
props: ['thoughts']
})
Vue.component('thoughts-to-ai-response', {
  delimiters: ["{(", ")}"],
  data: function() {
    return {'phrases': [{id: 1, phrase: ''}], response: ''}
  },
template: '<div>\
<h3>Thoughts to AI responses</h3>\
<table style="width:100%"><tr><th>Thought phrase</th><th>AI response</th></tr>\
<tr v-for="phrasesToAIResponse in phrasesToAIResponses"><td><ul><li  v-for="phrase in phrasesToAIResponse.phrases">{( phrase.phrase )}</li></ul></td><td>{( phrasesToAIResponse.response )}</td></tr>\
<tr><td style="width:45%"><ul><li v-for="phrase in phrases"><input v-model="phrase.phrase" type="text" /></li></ul></td><td style="width:50%"><textarea v-model="response"></textarea><button v-on:click="save">Save</button></td></tr>\
</table> \
</div>\
',
methods: {
  save: function() {
    $.post('/api/save_phrases_to_ai_response', {'phrases': JSON.stringify(this.phrases), 'response': this.response}, function(data) {
      app.phrasesToAIResponses = data;

    })
  }
},
props: ['phrasesToAIResponses']
})
  var users_public_uuid = '{{ public_uuid }}';
    var app = new Vue({
      delimiters: ["{(", ")}"],
      el: "#app",
      data: {
        users_public_uuid: users_public_uuid,
        users_have_access_to: [],
        checklists: {},
        thoughts: [],
        phrasesToAIResponses: [],
      },
      computed: {
        doesUserHaveAccessToAnyOtherUsers: function() {
          for (var i=0;i<this.users_have_access_to;i++) {
            if (this.users_have_access_to[i].public_uuid != this.users_public_uuid) {
              return true
            }
          }
          return false
        }
      },
      created: function() {
        $.get('/api/users_have_access_to', function(data) {
          app.users_have_access_to = data;
        })
        $.get('/api/profile', function(data) {
          if ('checklists' in data) {
            app.checklists = data.checklists;
          }
          if ('thoughts' in data) {
            app.thoughts = data.thoughts;

          }
          if ('phrases_to_ai_response' in data) {
            app.phrasesToAIResponses = data.phrases_to_ai_response;
          }
        })
      },
    });
  });
