import { defineStore } from 'pinia'

export const useNavbarStore = defineStore('navbar', {
    state: () => ({
        isSticky: false
    }),
    actions: {
        setIsSticky(isSticky: boolean) {
            this.isSticky = isSticky
        }
    }
})