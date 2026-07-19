import { NavLink,Outlet } from "react-router-dom"

function AdminLayout(){
    return(
        <div>
            <nav>
            <NavLink to="categories">カテゴリー</NavLink>
            <NavLink to="statuses">ステータス</NavLink>
            <NavLink to="jobs">職業</NavLink>
            <NavLink to="achievements">実績</NavLink>
            <NavLink to="rules">ルール</NavLink>
            <NavLink to="/">ホーム</NavLink>
            </nav>
            <Outlet />
        </div>
    )
}

export default AdminLayout