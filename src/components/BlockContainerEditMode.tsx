import React from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Switch from "@mui/material/Switch";
import FormControlLabel from "@mui/material/FormControlLabel";
import { getStylesForStyleType } from "../utils/helpers";

interface IBlockContainerProps {
  title: string;
  children: React.ReactNode;
  onToggleEditMode: (show: boolean) => void;
  isEditMode: boolean;
}

export const BlockContainerEditMode = ({
  title,
  children,
  onToggleEditMode,
  isEditMode
}: IBlockContainerProps) => {
  const containerStyles = getStylesForStyleType(
    { border: "1px solid #000" },
    { border: "1px solid #E0E0E0" }
  );

  const boxStyles = getStylesForStyleType(
    { padding: "17px 19px", borderBottom: "1px solid #A7A7A7" },
    { padding: "17px 19px", border: "1px solid #E0E0E0" }
  );

  return (
    <Box sx={containerStyles}>
      <Box sx={boxStyles}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}
        >
          <Typography
            data-testid="block-container-title"
            sx={{
              fontSize: "20px",
              fontWeight: 400,
              color: "#000"
            }}
          >
            {title}
          </Typography>
          <FormControlLabel
            control={
              <Switch
                checked={isEditMode}
                onClick={e => onToggleEditMode(!isEditMode)}
              />
            }
            label={
              isEditMode ? "Switch to Standard View" : "Switch to YAML Editor"
            }
          />
        </Box>
      </Box>
      {children}
    </Box>
  );
};
