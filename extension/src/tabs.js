import React, { useState } from "react";
import first_tab from "./first_tab.js";
import second_tab from "./second_tab.js";

const tabs = () => {
  const [activeTab, setActiveTab] = useState("tab1");
    //  Functions to handle Tab Switching
  const handleTab1 = () => {
    // update the state to tab12
    setActiveTab("tab1");
  };
  const handleTab2 = () => {
    // update the state to tab2
    setActiveTab("tab2");
  };
  return (
    <div className="tabs">
      {/* Tab nav */}
    <ul className="nav">
      <li
        className={activeTab === "tab1" ? "active" : ""}
        onClick={handleTab1}
      >
        Tab 1
      </li>
      <li
        className={activeTab === "tab2" ? "active" : ""}
        onClick={handleTab2}
      >
        Tab 2
      </li>
    </ul>
      <div className="outlet">
        {activeTab === "tab1" ? <first_tab /> : <second_tab />}
      </div>
    </div>
  );
};

export default tabs;