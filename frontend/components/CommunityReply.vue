<script setup lang="ts">
/**
 * One reply, and the replies to it.
 *
 * Recursive because a conversation is: someone answers a question, someone
 * else asks about the answer, and the first person comes back. A flat list can
 * hold all three and cannot say which remark is about which.
 *
 * Nesting is indented for two levels and then stops indenting. Past that the
 * thread is a conversation between two people rather than a tree, and column
 * width matters more than depth.
 */
const props = defineProps<{
  reply: any
  depth: number
  canAccept: boolean
  signedIn: boolean
  busy?: boolean
}>()
const emit = defineEmits<{
  vote: [id: number]
  accept: [id: number]
  report: [id: number]
  reply: [payload: { parentId: number; body: string; anonymous: boolean }]
}>()
const { $t } = useNuxtApp()

const open = ref(false)
const draft = ref('')
const anonymous = ref(false)

function send() {
  const body = draft.value.trim()
  if (!body) return
  emit('reply', { parentId: props.reply.id, body, anonymous: anonymous.value })
  draft.value = ''
  anonymous.value = false
  open.value = false
}

const who = computed(() =>
  props.reply.anonymous
    ? props.reply.is_mine
      ? $t('community.anonymousMine')
      : $t('community.anonymous')
    : props.reply.author
)
</script>

<template>
  <article class="reply" :class="{ 'reply--accepted': reply.is_accepted }">
    <p class="tiny muted byline">
      <span :class="{ anon: reply.anonymous }">{{ who }}</span>
      <span v-if="reply.is_accepted" class="tag"> {{ $t('community.acceptedBy') }}</span>
    </p>
    <p class="pre body">{{ reply.body }}</p>

    <div class="actions">
      <button
        class="like"
        :class="{ 'like--on': reply.viewer_voted }"
        type="button"
        :aria-pressed="reply.viewer_voted"
        @click="emit('vote', reply.id)"
      >{{ reply.viewer_voted ? '♥' : '♡' }} {{ reply.vote_count }}</button>

      <button v-if="signedIn" class="link" type="button" @click="open = !open">
        {{ $t('community.reply') }}
      </button>
      <button
        v-if="canAccept && !reply.is_accepted && depth === 0"
        class="link"
        type="button"
        @click="emit('accept', reply.id)"
      >{{ $t('community.markHelpful') }}</button>
      <button class="link" type="button" @click="emit('report', reply.id)">
        {{ $t('community.report') }}
      </button>
    </div>

    <div v-if="open" class="composer">
      <textarea
        v-model="draft"
        class="field"
        rows="3"
        :placeholder="$t('community.replyPlaceholder')"
      />
      <label class="anon-check">
        <input v-model="anonymous" type="checkbox" />
        <span>{{ $t('community.postAnonymously') }}</span>
      </label>
      <div class="composer-actions">
        <button class="btn btn--small" :disabled="busy" type="button" @click="send">
          {{ $t('community.postReply') }}
        </button>
        <button class="link" type="button" @click="open = false">
          {{ $t('community.cancel') }}
        </button>
      </div>
    </div>

    <div v-if="reply.replies?.length" class="children" :class="{ flat: depth >= 1 }">
      <CommunityReply
        v-for="child in reply.replies"
        :key="child.id"
        :reply="child"
        :depth="depth + 1"
        :can-accept="canAccept"
        :signed-in="signedIn"
        :busy="busy"
        @vote="emit('vote', $event)"
        @accept="emit('accept', $event)"
        @report="emit('report', $event)"
        @reply="emit('reply', $event)"
      />
    </div>
  </article>
</template>

<style scoped>
.reply { padding: var(--s3) 0; border-top: 1px solid var(--border); }
.reply:first-child { border-top: 0; }
.reply--accepted { background: var(--success-bg); border-radius: var(--radius-sm); padding: var(--s3); }

.byline { display: flex; gap: var(--s2); align-items: baseline; margin: 0 0 var(--s1); }
.anon { font-style: italic; }
.tag {
  background: var(--success-bg); color: var(--success);
  border-radius: var(--radius-pill); padding: 1px var(--s2); font-size: 0.7rem;
}
.body { margin: 0 0 var(--s2); }

.actions { display: flex; gap: var(--s3); align-items: center; }
.like {
  border: 1px solid var(--border-strong); background: var(--surface); color: var(--muted);
  border-radius: var(--radius-pill); padding: 2px var(--s3); font: inherit;
  font-size: 0.78rem; cursor: pointer; line-height: 1.6;
}
.like--on { color: var(--danger); border-color: var(--danger); background: var(--danger-bg); }
.like:hover { border-color: var(--danger); }
.link {
  border: 0; background: none; color: var(--muted); font: inherit; font-size: 0.78rem;
  cursor: pointer; padding: 0;
}
.link:hover { color: var(--blue); text-decoration: underline; }

.composer { display: grid; gap: var(--s2); margin-top: var(--s2); }
.field {
  width: 100%; padding: var(--s2) var(--s3); border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm); font: inherit; resize: vertical;
  background: var(--surface); color: var(--text);
}
.anon-check { display: flex; gap: var(--s2); align-items: center; font-size: 0.8rem; color: var(--muted); }
.composer-actions { display: flex; gap: var(--s3); align-items: center; }

/* Indent twice, then stop: past that it is two people talking, and the column
   is worth more than the depth. */
.children { margin-left: var(--s5); border-left: 2px solid var(--border); padding-left: var(--s3); }
.children.flat { margin-left: 0; border-left: 0; padding-left: 0; }

@media (max-width: 600px) {
  .children { margin-left: var(--s3); padding-left: var(--s2); }
}
</style>
