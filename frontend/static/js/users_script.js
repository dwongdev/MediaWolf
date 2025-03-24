import { socket } from './socket_script.js';

export class UserPage {
    constructor() {
        this.editUserModal = new bootstrap.Modal(document.getElementById('editUserModal'));
        this.newUserModal = new bootstrap.Modal(document.getElementById('newUserModal'));
        this.setupSocketListeners();
    }

    init() {
        this.setupEventListeners();
        this.fetchUsers();
    }

    setupEventListeners() {
        document.addEventListener("click", (event) => {
            if (event.target.classList.contains("editButton")) {
                const userId = event.target.closest("li").dataset.userId;
                this.editUser(userId);
            } else if (event.target.classList.contains("deleteButton")) {
                const userId = event.target.closest("li").dataset.userId;
                this.deleteUser(userId);
            }
        });

        document.getElementById("editUserForm").addEventListener("submit", (event) => {
            event.preventDefault();
            const userId = parseInt(document.getElementById("userId").value, 10);
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;
            const role = document.getElementById("role").value;

            socket.emit("save_user", { id: userId, name: username, password: password, role: role });
            this.editUserModal.hide();
            document.getElementById("newUserButton").focus();
        });

        document.getElementById("newUserForm").addEventListener("submit", (event) => {
            event.preventDefault();

            const name = document.getElementById("newUsername").value;
            const password = document.getElementById("newPassword").value;
            const role = document.getElementById("newRole").value;

            socket.emit("create_user", { id: "", name: name, password: password, role: role });
            this.newUserModal.hide();
            document.getElementById("newUserButton").focus();
        });
    }

    editUser(userId) {
        const userElement = document.querySelector(`[data-user-id="${userId}"]`);
        if (!userElement) return;

        const username = userElement.querySelector(".user-name").textContent.trim();
        const role = userElement.dataset.role;

        document.getElementById("userId").value = userId;
        document.getElementById("username").value = username;
        document.getElementById("password").value = "";
        document.getElementById("role").value = role;

        this.editUserModal.show();
    }

    deleteUser(userId) {
        const userElement = document.querySelector(`[data-user-id="${userId}"]`);
        if (!userElement) return;

        const username = userElement.querySelector(".user-name").textContent.trim();
        const role = userElement.dataset.role;

        if (confirm(`Are you sure you want to delete ${username}?`)) {
            socket.emit("delete_user", { id: userId, name: username, password: '', role: role });
        }
    }

    setupSocketListeners() {
        socket.on("user_created", () => {
            this.fetchUsers();
        });

        socket.on("user_updated", () => {
            this.fetchUsers();
        });

        socket.on("user_deleted", () => {
            this.fetchUsers();
        });

        socket.on("users_list", (data) => {
            this.renderUsers(data.users);
        });
    }

    fetchUsers() {
        socket.emit("get_users");
    }

    renderUsers(users) {
        const adminList = document.getElementById('adminList');
        const userList = document.getElementById('userList');

        adminList.innerHTML = '';
        userList.innerHTML = '';

        users.forEach(user => {
            const userElement = this.createUserElement(user);

            if (user.role === 'admin') {
                adminList.appendChild(userElement);
            } else {
                userList.appendChild(userElement);
            }
        });
    }

    createUserElement(user) {
        const template = document.getElementById('userTemplate');
        const userElement = template.content.cloneNode(true).querySelector("li");

        userElement.dataset.userId = user.id;
        userElement.dataset.role = user.role;
        userElement.querySelector(".user-name").textContent = user.name;

        return userElement;
    }
}
