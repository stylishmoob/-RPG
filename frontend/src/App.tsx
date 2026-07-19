import { BrowserRouter,Routes,Route,Navigate } from "react-router-dom";

import Home from "./pages/Home";
import Status from "./pages/Status";
import Category from "./pages/Category";
import History from "./pages/History";
import Login from "./pages/Login";
import Register from "./pages/Register";
import AdminLayout from "./pages/admin/AdminLayout";
import AdminCategories from "./pages/admin/AdminCategories";
import AdminAchievements from "./pages/admin/AdminAchievements";
import AdminJobs from "./pages/admin/AdminJobs";
import AdminRules from "./pages/admin/AdminRules";
import AdminStatuses from "./pages/admin/AdminStatuses";

function App(){
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Home />}/>
                <Route path="/status" element={<Status />}/>
                <Route path="/category" element={<Category />}/>
                <Route path="/history" element={<History />}/>
                <Route path="/login" element={<Login />}/>
                <Route path="/register" element={<Register />}/>
                <Route path="/admin" element={<AdminLayout/>}>
                    <Route index element={<Navigate to="categories" replace />}/>
                    <Route path="categories" element={<AdminCategories />} />
                    <Route path="statuses" element={<AdminStatuses />} />
                    <Route path="jobs" element={<AdminJobs />} />
                    <Route path="achievements" element={<AdminAchievements />} />
                    <Route path="rules" element={<AdminRules />} />
                </Route>

            </Routes>
        </BrowserRouter>
    );
}

export default App;