import { Component } from "react";
import CssBaseline from "@mui/material/CssBaseline";
import Container from "@mui/material/Container";
import { ThemeProvider } from "@mui/material/styles";
import Header from "./../../blog/Header.js";

import Footer from "./../../blog/Footer.js";
import Stack from "@mui/material/Stack";
import theme from "./../../blog/theme.js";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
// import Model from "./Model.js";
// import LinkButton from "./../../Custom/LinkButton.js";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";

import states from './../../Constants/States';

import CallbackKeyEventButton from '../../Custom/CallbackKeyEventButton';
import LinearProgress from '@material-ui/core/LinearProgress';

// function createData(contextName, humanResponse, prediction, metricOne, metricTwo) {
//     var metricTwoText = "YES";
//     if (metricTwo == 0){
//         metricTwoText == "NO";
//     }
//     return { contextName, humanResponse, prediction, metricOne, metricTwoText};
// }

// function createRows(){
//     var array = [];
//     for(var i = 0; i < this.state.ModelInfo.contextNames.length; i++) {
//         array.push(createData(this.state.ModelInfo.contextNames[i], this.state.ModelInfo.humanResponses[i], this.state.ModelInfo.predictions[i], this.state.ModelInfo.metricOne[i], this.state.ModelInfo.metricTwo[i]))
//     }

//     return array;
// }

// const rows = createRows();
// const avgSimScoreParam = Model.metricOne.length <= 0? 0 : Model.metricOne.reduce((a, b) => a + b) / Model.metricOne.length;
// const avgSuffSimParam = Model.metricOne.length <= 0? 0 : Model.metricTwo.reduce((a, b) => a + b) / Model.metricTwo.length * 100.0;

// class Results extends Component {
class DocResults extends Component {
	constructor(props) {
		super(props);

		this.state = {
			anchorEl: null,
			open: false,
			id: undefined,
			selectedContext: 0,
			processJustification: "",
			deploymentJustification: "",
			avgSimScore: 0,
			// 	Model.metricOne.length <= 0
			// 		? 0
			// 		: Model.metricOne.reduce((a, b) => a + b) / Model.metricOne.length,
			avgSuffSim: 0,
				// Model.metricOne.length <= 0
				// 	? 0
				// 	: (Model.metricTwo.reduce((a, b) => a + b) / Model.metricTwo.length) *
				// 	  100.0,
			// ModelInfo: Model,
            sectionComplete: true, /* TODO: interact with the page and decide when to allow the user to move on. */
		};
	}

    /**
    * When the component mounts, we save the annotations from open coding, and ask for them back. 
    * Asking for them back is more of an example, could techically just use locally saved state.
    
    * todo: see if this makes post less angry about database being locked
    */
    async componentDidMount () {
        try {
            // save the annotations before we ask for them
            await this.props.postData('/data/save_annotations', {"rows": this.props.loadAnnotations(), "id": this.props.getOptionID()});
            const data = await this.props.getDataWithParams('/data/get_annotations', {"id": this.props.getOptionID()});
            
            if (!data.ok) {
                throw Error(data.statusText);
            }

            // todo: begin considering how we'll gather which datas we should show for outputs
            // i'm figuring unlabeled data because 
            // const unlabeled_data = await this.props.getDataWithParams('/data/get_unlabeled_data', {"id": this.props.getOptionID()})
            // but this requires adding a backend method, so i'll do that in another branch.

        } catch (error) {
            console.log(error);
        }
    }

    onNextSubmit = () => {
        this.props.updateState(states.docView);
        // pass in states.{something}
    }

    /**
    * Callback function for next submit action.
    */
    // basically just have the option for the user to do a keyboard shortcut as well as button press.
    handleNextKeyPress = (event) => {
        if (event.key === ' ' && this.state.sectionComplete){
            this.onNextSubmit();
        }
    };

	createData(contextName, humanResponse, prediction, metricOne, metricTwo) {
		var metricTwoText = "YES";
		if (metricTwo === 0) {
			metricTwoText = "NO";
		}
		return { contextName, humanResponse, prediction, metricOne, metricTwoText };
	}

	createRows() {
		var array = [];
		// console.log(this.state.ModelInfo);
		// for (var i = 0; i < this.state.ModelInfo.contextNames.length; i++) {
		// 	array.push(
		// 		this.createData(
		// 			this.state.ModelInfo.contextNames[i],
		// 			this.state.ModelInfo.humanResponses[i],
		// 			this.state.ModelInfo.predictions[i],
		// 			this.state.ModelInfo.metricOne[i],
		// 			this.state.ModelInfo.metricTwo[i]
		// 		)
		// 	);
		// }

		return array;
	}

	render() {
		return (
			<ThemeProvider theme={theme}>
				<CssBaseline />
				<Container maxWidth="lg">
					<Header title="NLPDocTool" />
					<main>
						<Stack
							justifyContent="center"
							alignItems="center"
							spacing={4}
							sx={{ paddingTop: 10, paddingRight: 5, paddingLeft: 5 }}
						>
							<h2>Results from Running the Model </h2>
							<Typography variant="h6">Summary</Typography>
							<Box
								sx={{
									width: "100%",
									maxWidth: 900,
									bgcolor: "background.paper",
								}}
							>
								<TableContainer component={Paper}>
									<Table
										sx={{ minWidth: 650 }}
										aria-label="simple summary table"
									>
										<TableHead>
											<TableRow>
												<TableCell>Average Values </TableCell>
												<TableCell align="center">
													Similarity Score [0-1]
												</TableCell>
												<TableCell align="center">
													% With Sufficent Similarity
												</TableCell>
											</TableRow>
										</TableHead>
										<TableBody>
											<TableRow key={"averages"}>
												<TableCell component="th" scope="row"></TableCell>
												<TableCell align="center">
													{this.state.avgSimScore}
												</TableCell>
												<TableCell align="center">
													{this.state.avgSuffSim}
												</TableCell>
											</TableRow>
										</TableBody>
									</Table>
								</TableContainer>
							</Box>
							<Typography variant="h6">
								Think about your process. Why is this process ok?
							</Typography>
							<TextField
								inputProps={{
									cols: "50",
								}}
								multiline
								rows={3}
								fullWidth
								label="Process Justification"
								id="ProcessJustification"
								onChange={(event) => {
									this.setState({
										processJustification: event.target.value,
									});
								}}
							/>
							<Typography variant="h6">
								Here, you have created a model of an AI system. Think about how
								you generated your responses. Why can you justify deployment in
								this situation?
							</Typography>
							<TextField
								inputProps={{
									cols: "50",
								}}
								multiline
								rows={3}
								fullWidth
								label="Deployment Justification"
								id="DeploymentJustification"
								onChange={(event) => {
									this.setState({
										deploymentJustification: event.target.value,
									});
								}}
							/>
							<Typography variant="h6">Full Results</Typography>
							<Box
								sx={{
									width: "100%",
									maxWidth: 900,
									bgcolor: "background.paper",
								}}
							>
								<TableContainer component={Paper}>
									<Table sx={{ minWidth: 650 }} aria-label="simple table">
										<TableHead>
											<TableRow>
												<TableCell>Context Name </TableCell>
												<TableCell>What YOU Predicted</TableCell>
												<TableCell>What the MODEL Predicted </TableCell>
												<TableCell align="center">
													Similarity Score [0-1]
												</TableCell>
												<TableCell align="center">
													Sufficently Similar?
												</TableCell>
											</TableRow>
										</TableHead>
										<TableBody>
											{this.createRows().map((row) => (
												<TableRow key={row.contextName}>
													<TableCell component="th" scope="row">
														{row.contextName}
													</TableCell>
													<TableCell align="center">
														{row.humanResponse}
													</TableCell>
													<TableCell align="center">{row.prediction}</TableCell>
													<TableCell align="center">{row.metricOne}</TableCell>
													<TableCell align="center">
														{row.metricTwoText}
													</TableCell>
												</TableRow>
											))}
										</TableBody>
									</Table>
								</TableContainer>
							</Box>

							{/* <LinkButton
								to="/NLPDocTool/viewDoc"
								onClick={() => {
									// Model.processJustification = this.state.processJustification;
									// Model.deploymentJustification =
									// 	this.state.deploymentJustification;
									// console.log(Model);
								}}
								variant="contained"
							>
								View Documentation
							</LinkButton> */}
                            <div style={{ marginTop: "15px", width: "100%" }}>
                                <CallbackKeyEventButton
                                    callBackFunc={this.handleNextKeyPress}
                                    buttonAvailable={this.state.sectionComplete}
                                    clickFunc={this.onNextSubmit}
                                    text={"View Documentation (space)"}
                                />
                            </div>
						</Stack>
					</main>
				</Container>

				<Footer title="Designed By" description="XXX" />
			</ThemeProvider>
		);
	}
}

// export default Results;
export default DocResults;