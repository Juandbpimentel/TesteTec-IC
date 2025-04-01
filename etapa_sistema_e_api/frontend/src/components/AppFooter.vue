<template>
  <v-footer height="40" app>
    <a
      v-for="item in items"
      :key="item.title"
      :href="item.href"
      :title="item.title"
      class="d-inline-block mx-2 social-link"
      rel="noopener noreferrer"
      target="_blank"
    >
      <v-icon
        :icon="item.icon"
        :size="item.icon === '$vuetify' ? 24 : 16"
      />
    </a>

    <v-divider
      class="mx-4"
      vertical
      color="rgba(var(--v-theme-on-background), var(--v-divider-opacity))"
      height="24"
      inset
      width="1"
    />

    <div class="d-flex align-center">
      <span class="d-none d-sm-inline-block">Juan Pimentel</span>
    </div>
  </v-footer>
</template>

<script setup>
  const items = [
    {
      title: 'Meu GitHub',
      icon: `mdi-github`,
      href: 'https://github.com/Juandbpimentel',
    },
    {
      title: 'Meu LinkedIn',
      icon: `mdi-linkedin`,
      href: 'https://www.linkedin.com/in/juan-pimentel-3b6a67221/',
    }
  ]
</script>

<style scoped lang="sass">
  .social-link :deep(.v-icon)
    color: rgba(var(--v-theme-on-background), var(--v-disabled-opacity))
    text-decoration: none
    transition: .2s ease-in-out

    &:hover
      color: rgba(25, 118, 210, 1)

    .footer-name
      color: rgba(var(--v-theme-on-background), var(--v-disabled-opacity))
      font-size: 14px
      font-weight: 500
</style>
