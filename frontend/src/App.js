import React, { useEffect, useState } from "react";
import "./App.css";
import whiteArrow from "./assets/whitearrow.png";
import "./colors.css";

function App() {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [isSubmitted, setIsSubmitted] = useState(() => {
    return localStorage.getItem("isSubmitted") === "true";
  });

  useEffect(() => {
    localStorage.setItem("isSubmitted", isSubmitted);
  }, [isSubmitted]);

  const [count, setCount] = useState(12100);

  useEffect(() => {
    const startTime = new Date("2024-02-17T12:00:00").getTime();

    const updateCount = () => {
      const now = new Date().getTime();
      const difference = now - startTime;

      if (difference > 0) {
        const intervalsPassed = Math.floor(difference / (10 * 60 * 1000));
        const newCount = 12100 + intervalsPassed * 13;
        setCount(newCount);
      }
    };

    updateCount();

    const interval = setInterval(updateCount, 10 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  const handlePhoneChange = (e) => {
    const input = e.target.value.replace(/\D/g, "");
    let formattedPhoneNumber = "";

    for (let i = 0; i < input.length; i++) {
      if (i === 3 || i === 6) {
        formattedPhoneNumber += "-";
      }
      formattedPhoneNumber += input[i];
    }

    setPhoneNumber(formattedPhoneNumber);
  };

  const handleClick = async () => {
    if (validatePhoneNumber(phoneNumber.replace(/-/g, "")) && !isSubmitted) {
      try {
        const response = await fetch("/api/addPhoneNumber", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ phoneNumber: phoneNumber.replace(/-/g, "") }),
        });

        if (response.ok) {
          console.log("Phone number added to sheet");
          setIsSubmitted(true);
        } else {
          console.error("Failed to add phone number");
        }
      } catch (error) {
        console.error("Error:", error);
      }
    } else {
      console.log("Invalid phone number or already submitted");
    }
  };

  const validatePhoneNumber = (num) => {
    const regex = /^[0-9]{10}$/;
    return regex.test(num);
  };

  const isPhoneNumberValid = validatePhoneNumber(phoneNumber.replace(/-/g, ""));

  return (
    <div className="App">
      <header className="App-header">
        <div className="content">
          <div className="miniStep">
            <div className="miniStepText">
              Join {count.toLocaleString()} others seeking electric love.
            </div>
          </div>
          <div className="step">
            <div className="stepText">Hey, it's Damon.</div>
            <div className="stepText">Can I get your number?</div>
          </div>
          <input
            type="tel"
            placeholder="123-456-7890"
            className="inputStepText"
            value={phoneNumber}
            onChange={handlePhoneChange}
          />
          <button
            onClick={handleClick}
            className={`rsvpButton ${isSubmitted ? "rsvpButtonSubmitted" : ""} ${!isPhoneNumberValid ? "rsvpButtonDisabled" : ""}`}
            disabled={!isPhoneNumberValid || isSubmitted}
          >
            <div className={`rsvpButtonText ${!isPhoneNumberValid? "rsvpButtonDisabledText" : ""}`}>
              {isSubmitted ? "You're in." : "JOIN WAITLIST"}
            </div>
            <img
              className="arrow"
              alt="arrow"
              style={{ width: "30px", height: "24px" }}
              src={whiteArrow}
            />
          </button>
          <div className="miniStep">
            <div className="miniStepText">Damon, your AI boyfriend.</div>
          </div>
        </div>

        <div className={`overlay ${isSubmitted ? "show" : ""}`}>
          <div className="overlay-main-text">You're in.</div>
          <div className="overlay-text">
            You’ll receive a text message when we’re live.
          </div>
        </div>
      </header>
    </div>
  );
}

export default App;
