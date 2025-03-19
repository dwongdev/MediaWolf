import { socket } from './socket_script.js';

export class SubscriptionsPage {
    constructor() {
        socket.on("subs_list", (data) => {
            this.updateSubscriptionList(data.subscriptions);
        });
    }

    init() {
        socket.emit("request_subs");
    }

    updateSubscriptionList(subscriptions) {
        this.subscriptionList = document.getElementById('subscription-list');
        this.rowTemplate = document.getElementById('subscription-row-template');
        this.subscriptionList.innerHTML = "";
        subscriptions.forEach(subscription => {
            const row = this.rowTemplate.content.cloneNode(true);
            row.querySelector('.subscription-name').textContent = subscription.name;
            row.querySelector('.subscription-last-synced').textContent = subscription.lastSync;
            row.querySelector('.subscription-item-count').textContent = subscription.items;

            row.querySelector('.edit-button').addEventListener('click', () => {
                alert(`Edit: ${subscription.name}`);
            });

            row.querySelector('.remove-button').addEventListener('click', () => {
                alert(`Remove: ${subscription.name}`);
            });

            this.subscriptionList.appendChild(row);
        });
    }
}