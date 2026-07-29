import { NavLink,Outlet } from "react-router-dom"
import styles from "../../styles/admin/AdminLayout.module.css";

function AdminLayout(){
    return(
        <div className={styles.layout}>
            <nav className={styles.nav}>
            <NavLink className={styles.link} to="categories">カテゴリー</NavLink>
            <NavLink className={styles.link} to="statuses">ステータス</NavLink>
            <NavLink className={styles.link} to="jobs">職業</NavLink>
            <NavLink className={styles.link} to="achievements">実績</NavLink>
            <NavLink className={styles.link} to="rules">ルール</NavLink>
            <NavLink className={styles.link} to="users">ユーザー</NavLink>
            <NavLink className={styles.link} to="/">ホーム</NavLink>
            </nav>
            <main className={styles.content}>
                <Outlet />
            </main>
        </div>
    )
}

export default AdminLayout
