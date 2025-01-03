import React, { useState, useRef, useEffect, RefObject } from "react";
import { Outlet, useOutletContext } from "react-router-dom";
import Box from "@mui/material/Box";
import { Popup } from "../components";
import { Environments } from "../features/environments";
import { StyledScrollContainer } from "../styles";
import { useAppDispatch, useAppSelector } from "../hooks";
import { closeNotification } from "../features/notification/notificationSlice";

export const PageLayout = () => {
  const dispatch = useAppDispatch();
  const [refreshEnvironments, setRefreshEnvironments] = useState(false);
  const notification = useAppSelector(state => state.notification);
  const scrollRef = useRef<HTMLDivElement>(null);

  // TODO remove this coupling between notifications and environment refreshes.
  // This use of state to refetch the environment is an anti-pattern. We should
  // leverage RTK's cache invalidation features instead.
  useEffect(() => {
    setRefreshEnvironments(true);
  }, [notification]);

  return (
    <Box
      sx={{
        display: "grid",
        gridTemplateColumns: "minmax(max-content, 275px) 1fr",
        gridTemplateRows: "100%",
        width: "100%",
        height: "100%",
        background: "#FFF"
      }}
    >
      <Environments
        refreshEnvironments={refreshEnvironments}
        onUpdateRefreshEnvironments={setRefreshEnvironments}
      />
      <StyledScrollContainer
        ref={scrollRef}
        sx={{
          backgroundColor: "#F9F9F9",
          height: "100%",
          overflowY: "scroll"
        }}
      >
        <Outlet context={scrollRef} />
      </StyledScrollContainer>
      <Popup
        isVisible={notification.show}
        description={notification.description}
        onClose={() => dispatch(closeNotification())}
      />
    </Box>
  );
};

// TypeScript-friendly version of the useOutletContext() hook
export function useScrollRef() {
  return useOutletContext<RefObject<HTMLDivElement>>();
}
