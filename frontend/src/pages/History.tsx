import{ useState,useRef,useEffect } from "react";
import { Link,useNavigate } from "react-router-dom";
import Chart from "Chart.js/auto";
import type { PeriodType,UnitType,HistoryDataType } from "../types/api";
import "../styles/history.css";

const unitLabels ={
        seconds: "活動時間(秒)",
        minutes: "活動時間(分)",
        hours: "活動時間(時間)",
    };
    
function History() {
    const [historyData,setHistoryData] = useState<HistoryDataType | null>(null);

    const navigate=useNavigate();

    const [ctx1Period,setCtx1Period] = useState<PeriodType>("all");
    const [ctx1Unit,setCtx1Unit] = useState<UnitType>("hours");

    const [ctx2Period,setCtx2Period] = useState<PeriodType>("all");
    const [ctx2Unit,setCtx2Unit] = useState<UnitType>("hours");

    const categoryChartRef = useRef<HTMLCanvasElement | null>(null);
    const dailyCategoryChartRef = useRef<HTMLCanvasElement | null>(null);

    useEffect(() => {
        async function fetchHistoryData(){
            try{
                const response = await fetch(
                    `/api/history?ctx1Period=${ctx1Period}&ctx2Period=${ctx2Period}`);
                if(response.status === 401){
                    navigate("/login");
                    return;
                }
                if(!response.ok){
                    throw new Error("データの取得に失敗しました");
                }
                const data: HistoryDataType = await response.json();
                setHistoryData(data);
            } catch (error){
                console.error(error);
            }
        }
        fetchHistoryData();
        },[
            ctx1Period,
            ctx2Period,
            navigate,
        ]);

    

    useEffect(() =>{
        if(!historyData || !categoryChartRef.current) return;

        const categorySummary = historyData.categorySummary;

        const categoryLabels = categorySummary.map((category) =>
           category.category_name );

        const categoryValues = categorySummary.map((category) =>
            {switch(ctx1Unit) {
                case "seconds":
                    return category.category_total_seconds;
                case "minutes": 
                    return category.category_total_seconds /60;
                case "hours": 
                    return category.category_total_seconds /3600;
                default:
                    return 0;
            }});

        const label = unitLabels[ctx1Unit];

        const chart = new Chart(categoryChartRef.current, {
            type:"bar",
            data:{
            labels:categoryLabels,
            datasets:[{
            label:label,  
            data:categoryValues,
            }]
        },
    })
        return () =>{
            chart.destroy();
        };
    },[historyData,ctx1Unit]);

    useEffect(() =>{
        if(!historyData || !dailyCategoryChartRef.current) return;

        const dailyCategorySummary = historyData.dailyCategorySummary;

        const dailyCategoryLabels = dailyCategorySummary.map((date) =>
           date.log_date );

        const dailyCategoryValues = dailyCategorySummary.map((date) =>
            {switch(ctx2Unit) {
                case "seconds":
                    return date.daily_total_seconds;
                case "minutes": 
                    return date.daily_total_seconds /60;
                case "hours": 
                    return date.daily_total_seconds /3600;
                default:
                    return 0;
            }});

        const label = unitLabels[ctx2Unit];

        const chart = new Chart(dailyCategoryChartRef.current, {
            type:"bar",
            data:{
            labels:dailyCategoryLabels,
            datasets:[{
            label:label,  
            data:dailyCategoryValues,
            }]
        },
    })
        return () =>{
            chart.destroy();
        };
    },[historyData,ctx2Unit]);

    if(!historyData){
        return <div>loading...</div>;
    }

    return (
        <div className="main">
            <div className="maininner">
                <div className="card">
                    <h2>カテゴリー別活動時間</h2>
                    <canvas ref={categoryChartRef}></canvas>
                    
                    <select 
                        className="ctx1_period" 
                        onChange={(e) =>
                            setCtx1Period(e.target.value as PeriodType)
                        }
                    >
                        <option value="all">全期間</option>
                        <option value="today">今日</option>
                        <option value="7days">直近7日</option>
                        <option value="week">今週</option>
                        <option value="month">今月</option>
                        <option value="year">今年</option>
                    </select>

                    <select 
                        className="ctx1_unit" 
                        onChange={(e) =>
                            setCtx1Unit(e.target.value as UnitType)
                        }
                    >
                        <option value="seconds">秒</option>
                        <option value="minutes">分</option>
                        <option value="hours">時間</option>
                    </select> 
                </div>
                <div className="card">
                    <h2>日別活動時間</h2>
                    <canvas ref={dailyCategoryChartRef}></canvas>
                    
                    <select 
                        className="ctx2_period" 
                        onChange={(e) =>
                        setCtx2Period(e.target.value as PeriodType)
                        }
                    >
                        <option value="all">全期間</option>
                        <option value="today">今日</option>
                        <option value="7days">今週</option>
                        <option value="month">今月</option>
                        <option value="year">今年</option>
                    </select>

                    <select 
                        className="ctx2_unit" 
                        onChange={(e) =>
                        setCtx2Unit(e.target.value as UnitType)
                        }
                    >
                        <option value="seconds">秒</option>
                        <option value="minutes">分</option>
                        <option value="hours">時間</option>
                    </select>
                </div>
                <div className="link">
                    <Link to="/">ホームへ</Link>
                </div>
            </div>
        </div>
    )
}

export default History;